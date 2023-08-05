import json
import typing
import aiohttp
from dapr.clients import MetadataTuple
from dapr.conf import settings
from fastapi import HTTPException, Request
from wisdoms_dapr import consts, schemas



class EnforceRequestForwarder(object):
    """Enforce Request Forwarder"""

    def __init__(
        self,
        service_name: str,
        service_mode: schemas.ServiceRunMode,
        service_version: str,
        enforce_app_id: str,
        enforce_route_service_method: str = "v1/enforce/route/forward",
        enforce_authz_service_method: str = "v1/enforce/authz",
        enforce_url_path_whitelist: typing.Optional[list[str]] = None,
        enforce_request_verb_whitelist: typing.Optional[list[str]] = None,
    ) -> None:
        self.service_name = service_name
        self.service_mode = service_mode
        self.service_version = service_version
        self.enforce_app_id = enforce_app_id
        self.enforce_url_path_whitelist: set[str] = set(
            enforce_url_path_whitelist or []
        )
        self.enforce_request_verb_whitelist: set[str] = set(
            enforce_request_verb_whitelist or []
        )
        self.enforce_route_service_method = enforce_route_service_method
        self.enforce_authz_service_method = enforce_authz_service_method
        self.MAX_REQUEST_COUNT = 3
        self.session_timeout = aiohttp.ClientTimeout(
            total=settings.DAPR_HTTP_TIMEOUT_SECONDS
        )
        self.session = aiohttp.ClientSession(timeout=self.session_timeout)

    async def forward(
        self, request: Request, data: typing.Any = None
    ) -> typing.Optional[bool]:
        """转发授权请求，包括：路由授权和对象授权

        :param request: 请求
        :param data: 数据

        :return bool: bool表示验证结果，None未进行验证
        """

        path = request.url.path
        verb = request.method.upper()

        # 跳过特定的请求方法
        if verb in self.enforce_request_verb_whitelist:
            return None

        # 跳过特定的方法
        if path in self.enforce_url_path_whitelist:
            return None

        # 生成转发请求metadata
        metadata: MetadataTuple = tuple(
            [(k, v) for k, v in request.headers.items()]
            + [
                # Service Info
                (
                    consts.ENFORCE_REQUEST_FORWARD_HEADER_NAME_SERVICE_NAME,
                    self.service_name,
                ),
                (
                    consts.ENFORCE_REQUEST_FORWARD_HEADER_NAME_SERVICE_RUN_MODE,
                    self.service_mode.value,
                ),
                (
                    consts.ENFORCE_REQUEST_FORWARD_HEADER_NAME_SERVICE_VERSION,
                    self.service_version,
                ),
                # Forward Info
                (
                    consts.ENFORCE_REQUEST_FORWARD_HEADER_NAME_URL,
                    str(request.url),
                ),
                (
                    consts.ENFORCE_REQUEST_FORWARD_HEADER_NAME_VERB,
                    verb,
                ),
            ]
        )
        # 处理data
        if data:
            # 此时表明是转发授权请求
            data = json.dumps(data)
            method_name = self.enforce_authz_service_method
        else:
            method_name = self.enforce_route_service_method

        # NOTE: `Content-length` header will block request
        headers = dict(metadata)
        [headers.pop(h, None) for h in ["content-length", "connection"]]
        # NOTE: starlette不支持中间件读取body
        # data=await request.body(),
        data = ""
        #TODO 转发会失败？
        max_request_count = self.MAX_REQUEST_COUNT
        while max_request_count > 0:
            async with self.session.post(
                f"http://{settings.DAPR_RUNTIME_HOST}:{settings.DAPR_HTTP_PORT}/{settings.DAPR_API_VERSION}/invoke/{self.enforce_app_id}/method/{method_name}",
                data=data,
                headers=headers,
            ) as resp:
                if resp.status == 500 and "errorCode" in await resp.json():
                    max_request_count -= 1
                    if max_request_count == 0:
                        resp_result = await resp.text()
                        raise HTTPException(status_code=resp.status, detail=resp_result)
                elif resp.status != 200:
                    resp_result = await resp.text()
                    raise HTTPException(status_code=resp.status, detail=resp_result)
                else:
                    return await resp.json()
        # async with self.session.post(
        #     f"http://{settings.DAPR_RUNTIME_HOST}:{settings.DAPR_HTTP_PORT}/{settings.DAPR_API_VERSION}/invoke/{self.enforce_app_id}/method/{method_name}",
        #     data=data,
        #     headers=headers,
        # ) as resp:
        #     if resp.status == 200:
        #         return await resp.json()
        #     else:
        #         resp_result = await resp.text()
        #         raise HTTPException(status_code=resp.status, detail=resp_result)