import asyncio
import datetime
import enum
import json
import os
import typing
from threading import Lock

import fastapi
from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp
from wisdoms_dapr import consts, deps, schemas
from wisdoms_dapr.common.enforce import EnforceRequestForwarder
from wisdoms_dapr.consts import ENV_NAME_SERVICE_RUN_MODE, ENV_NAME_SERVICE_VERSION
from wisdoms_dapr.exceptions import ServiceErrorException
from wisdoms_dapr.schemas.base import ServiceRunMode


class RouteType(str, enum.Enum):
    """路由类型"""

    normal = "normal"
    crontab = "crontab"


class AuthorizationType(str, enum.Enum):
    """
    Authorization Type
    """

    route = "route"
    authz = "authz"


class ServiceRouteInfo(BaseModel):
    """服务路由信息"""

    id: typing.Optional[str]
    path: str
    verb: str
    desc: typing.Optional[str]
    type: RouteType = RouteType.normal  # 路由类型


class AuthzIdentityData(BaseModel):
    """Authz Identity Data"""

    id: typing.Optional[int] = None


class ServiceAuthzInfo(BaseModel):
    """服务授权信息"""

    name: str
    data: typing.Any = None
    identity: typing.Optional[AuthzIdentityData]
    desc: typing.Optional[str]


class ServiceRegisterInfo(BaseModel):
    """服务注册信息"""

    app_id: str
    version: str
    mode: schemas.ServiceRunMode = schemas.ServiceRunMode.dev
    server: typing.Literal["FastAPI", "Django", "Flask"] = "FastAPI"
    desc: typing.Optional[str]
    timestamp: int
    routes: list[ServiceRouteInfo]
    authz: list[ServiceAuthzInfo] = []


def extract_fastapi_route_info(
    app: fastapi.FastAPI,
    exclude_verbs: typing.Optional[set[str]] = None,
    check_unique: bool = False,
) -> list[ServiceRouteInfo]:
    """提取FastAPI路由信息

    :param app: FastAPI实例
    :param exclude_verbs: 排除的HTTP方法
    :param check_unique: 是否检查路由是否重复
    """

    result: list[ServiceRouteInfo] = []
    if not exclude_verbs:
        exclude_verbs = set()

    all_routes: set[str] = set()
    for r in app.router.routes:
        allow_verbs = r.methods - exclude_verbs
        for v in allow_verbs:
            # 检查注册路由是否重复
            if check_unique:
                permission = "&".join([v.upper(), r.path])
                if permission in all_routes:
                    raise ValueError(f"Duplicate route: {permission}")

            result.append(
                ServiceRouteInfo(
                    id=getattr(r, "unique_id", None),
                    path=r.path,
                    verb=v,
                    desc=getattr(r, "description", None),
                    type=RouteType.crontab
                    if deps.ScheduleTaskRegister.find_route_schedule_dependency(r)
                    else RouteType.normal,
                )
            )

    return result


def extract_service_mode() -> schemas.ServiceRunMode:
    """提取服务模式"""

    mode = os.getenv(ENV_NAME_SERVICE_RUN_MODE)
    for m in ServiceRunMode:
        if m.value == mode:
            return m
    else:
        return ServiceRunMode.dev


def extract_service_version_info() -> str:
    """提取服务版本信息"""

    r = os.getenv(ENV_NAME_SERVICE_VERSION, "")
    if not r:
        return "0.0.1"
    return r.strip()


def get_app_id() -> str:
    """获取服务ID"""

    return os.environ.get(consts.ENV_NAME_DAPR_APP_ID, "")


class EnforceAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: ASGIApp, enforce_forwarder: EnforceRequestForwarder
    ) -> None:
        self.enforce_forwarder = enforce_forwarder
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:

        # 预处理
        r = await self.enforce_forwarder.forward(request)
        print("enforce result:", r)

        if r or r is None:
            resp = await call_next(request)
        else:
            resp = JSONResponse(
                status_code=403, content={"detail": "Permission Forbidden"}
            )

        return resp


class FastAPIServiceRegister(object):
    """FastAPI Service Register

    设计：
    - 注册服务接口，方便对服务权限的管理
    - 提取服务中存在的定时调度依赖，用于定时任务的注册
    - 初始化服务运行相关环境变量，如：服务端口，dapr相关端口等
    """

    exclude_http_verbs: set[str] = {"OPTION", "HEAD"}

    service_register_topic_name = consts.EVENT_TOPIC_NAME_SERVICE_REGISTER
    service_register_subscribe_route = consts.EVENT_SUBSCRIBE_ROUTE_SERVICE_REGISTER

    def __init__(
        self,
        app: FastAPI,
        app_id: str = "",
        run_mode: typing.Optional[schemas.ServiceRunMode] = None,
        version: str = "",
        desc: typing.Optional[str] = "",
        *,
        subscribe_infos: typing.Optional[list[schemas.DaprSubscribeInfoItem]] = None,
        pubsub_name: str = consts.DEFAULT_PUBSUB_NAME,
        schedule_tasks_register_method_name: str = "v1/schedule/register",
        schedule_tasks_remove_method_name: str = "v1/schedule/remove",
        remove_schedule_tasks_on_shutdown: bool = False,
        # enforce params
        enable_route_auth: bool = False,
        enforce_app_id: str = consts.SERVICE_NAME_POLICY,
        enforce_authz_service_method: str = "v1/enforce/authz",
        enforce_route_service_method: str = "v1/enforce/route/forward",
        enforce_url_path_extra_whitelist: typing.Optional[list[str]] = None,
        enforce_request_verb_whitelist: typing.Optional[list[str]] = None,
    ) -> None:
        """
        初始化服务注册器

        :param app: FastAPI app实例
        :param app_id: 注册的服务名称
        :param run_mode: 运行模式，如果未指定读取环境变量，如果未指定环境变量则默认为开发模式
        :param version: 服务版本，默认版本为：0.0.1
        :param desc: 服务描述
        :param pubsub_name: pubsub名称
        :param schedule_tasks_register_method_name: 定时任务注册接口名称
        :param schedule_tasks_remove_method_name: 定时任务移除接口名称
        :param remove_schedule_tasks_on_shutdown: 当服务关闭时是否移除定时任务
        :param enable_route_auth: 是否启用路由权限控制
        :param enforce_app_id: 权限控制Dapr服务的appid
        :param enforce_authz_service_method: 授权检查接口名称
        :param enforce_route_service_method: 路由检查接口名称
        :param enforce_url_path_extra_whitelist: 额外路由检查的URL路径白名单，跳过白名单路由检查
        :param enforce_request_verb_whitelist: 额外路由检查的请求方法白名单，跳过白名单路由检查，verb须全部大写
        """

        self.app = app
        if not app_id:
            app_id = get_app_id()

        if not app_id:
            raise ServiceErrorException(
                f"get dapr `app_id` failed, please set `APP_ID` in env variables or set app_id value in {self.__class__.__name__} __init__ function."
            )

        # Dapr APP ID
        self.app_id = app_id

        # Service Run Mode
        if run_mode is None:
            self.run_mode = extract_service_mode()
        else:
            self.run_mode = run_mode

        # Service Version
        if not version:
            self.version = extract_service_version_info()

        self.desc = desc
        self.subscribe_infos = subscribe_infos
        self.pubsub_name = pubsub_name

        self.schedule_tasks_register_method_name = schedule_tasks_register_method_name
        self.schedule_tasks_remove_method_name = schedule_tasks_remove_method_name
        self.remove_schedule_tasks_on_shutdown = remove_schedule_tasks_on_shutdown

        self.lock = Lock()
        self.is_registered: bool = False

        # 是否启用路由权限控制
        self.enforce_forwarder = None
        if enable_route_auth:
            self.enforce_forwarder = EnforceRequestForwarder(
                service_name=self.app_id,
                service_mode=self.run_mode,
                service_version=self.version,
                enforce_app_id=enforce_app_id,
                enforce_authz_service_method=enforce_authz_service_method,
                enforce_route_service_method=enforce_route_service_method,
                enforce_url_path_whitelist=consts.ENFORCE_REQUEST_FORWARD_WHITELIST_URL_PATH.copy()
                + (enforce_url_path_extra_whitelist or []),
                enforce_request_verb_whitelist=enforce_request_verb_whitelist
                or consts.ENFORCE_REQUEST_FORWARD_WHITELIST_VERB,
            )

            # 添加授权转发中间件
            self.app.middleware("http")(self.enforce_route_permission_middleware)
            # self.app.add_middleware(
            #     EnforceAuthMiddleware, enforce_forwarder=self.enforce_forwarder
            # )

    async def enforce_route_permission_middleware(
        self,
        request: Request,
        call_next: typing.Callable[[Request], typing.Any],
    ):
        """应用策略中间件"""

        if not self.enforce_forwarder:
            return await call_next(request)
        # 调用策略微服务执行策略验证
        try:
            r = await self.enforce_forwarder.forward(request)
        except HTTPException as e:
            try:
                detail = json.loads(e.detail)
            except Exception:
                detail = {"detail": str(e.detail)}

            return JSONResponse(
                content=detail,
                status_code=e.status_code,
            )
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=500,
                content={"detail": f"enforce authz service timeout"},
            )
        except Exception as e:
            import traceback

            traceback.print_exc()

            # 调用授权请求失败
            return JSONResponse(
                content={"detail": f"Enforce route permission failed: {e}"},
                status_code=500,
            )
        else:
            # 授权通过
            if r is None or r.get("allow"):
                return await call_next(request)

            # 授权失败
            return JSONResponse(
                content={"detail": r.get("detail", "Permission denied")}, status_code=r.get("status_code", 403)
            )

    def get_register_service_info_subscribe_info(
        self,
    ) -> schemas.DaprSubscribeInfoItem:
        """注册服务注册订阅路由并返回注册服务信息订阅信息"""

        return schemas.DaprSubscribeInfoItem(
            topic=self.service_register_topic_name,
            pubsubname=self.pubsub_name,
            route=self.service_register_subscribe_route,
        )

    def add_dapr_subscribe_route(self):
        """添加dapr订阅路由"""

        # 获取调度路由订阅信息
        infos = deps.ScheduleTaskRegister(
            self.app_id,
            app=self.app,
            schedule_tasks_register_method_name=self.schedule_tasks_register_method_name,
            schedule_tasks_remove_method_name=self.schedule_tasks_remove_method_name,
            remove_schedule_tasks_on_shutdown=self.remove_schedule_tasks_on_shutdown,
        ).get_schedule_subscribe_schemas()

        # 添加服务注册订阅信息
        infos.append(self.get_register_service_info_subscribe_info())

        # 添加服务自定义订阅路由
        if self.subscribe_infos:
            infos.extend(self.subscribe_infos)

        # 添加dapr订阅注册路由
        if infos:
            self.app.get("/dapr/subscribe", tags=[consts.ROUTE_TAG_NAME_AUTO_REGISTER])(
                lambda: infos
            )

    def extract_register_info(self) -> ServiceRegisterInfo:
        """提取服务注册信息"""

        route_infos = extract_fastapi_route_info(
            app=self.app,
            exclude_verbs=self.exclude_http_verbs,
            check_unique=True,
        )

        # TODO: 提取授权信息
        return ServiceRegisterInfo(
            app_id=self.app_id,
            version=self.version,
            mode=self.run_mode,
            desc=self.desc,
            timestamp=int(datetime.datetime.now().timestamp()),
            routes=route_infos,
        )

    def register_to_policy_service(self):
        """注册到policy服务"""

        print("service_register event ...")
        with self.lock:

            if self.is_registered:
                return

            register_info = self.extract_register_info()
            with DaprClient() as client:
                try:
                    client.invoke_method(
                        app_id=consts.SERVICE_NAME_POLICY,
                        method_name=consts.INVOKE_ROUTE_POLICY_SERVICE_SCHEDULE_TASK_REGISTER,
                        data=register_info.json(),
                        content_type=consts.CONTENT_TYPE_JSON,
                        http_verb=consts.HTTP_VERB_POST,
                        metadata=None,
                    )
                    self.is_registered = True
                except Exception as e:
                    print("catch service register exception:", e)

    def register(self):
        """注册服务信息

        提取服务信息，并将其添加到服务的订阅事件中

        不直接调用接口注册的原因：dapr依赖服务先启动，而直接注册则要求dapr先启动，存在双向依赖
        """

        # 添加Dapr订阅路由
        self.add_dapr_subscribe_route()

        # 添加服务信息获取订阅路由，目的是订阅服务注册事件并借此上报服务信息
        # NOTE: 所有路由注册操作，必须先于注册信息提取
        self.app.post(
            "/" + self.service_register_subscribe_route,
            tags=[consts.ROUTE_TAG_NAME_AUTO_REGISTER],
        )(self.register_to_policy_service)

    def __call__(self):
        self.register()
