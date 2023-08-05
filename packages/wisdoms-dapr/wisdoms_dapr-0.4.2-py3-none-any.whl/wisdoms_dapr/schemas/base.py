import enum
import typing

from pydantic import BaseModel, Field, create_model_from_typeddict
from pydantic.generics import GenericModel
from wisdoms_dapr.elasticsearch.searches import ESSearchResult

GenericSchema = typing.TypeVar("GenericSchema", bound=BaseModel)
PaginationResultDataType = typing.TypeVar(
    "PaginationResultDataType",
    bound=typing.Union[dict[str, typing.Any], BaseModel],
)

IdType = typing.TypeVar('IdType', bound=typing.Union[int, str])


class IdSchema(GenericModel, typing.Generic[IdType]):
    id: IdType


class IdsSchema(GenericModel, typing.Generic[IdType]):
    ids: list[IdType]


class PaginationResultSchema(
    GenericModel, typing.Generic[PaginationResultDataType]
):
    """Pagination List Result Schema"""

    page: int
    size: int
    total: int
    data: typing.Optional[typing.List[PaginationResultDataType]]


class PaginationSchema(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1)
    sort: typing.Optional[str]
    query: typing.Optional[str]

    def get_page_slice(self):
        return slice((self.page - 1) * self.size, self.page * self.size)


class ServiceRunMode(str, enum.Enum):
    """服务运行模式"""

    default = ''
    prod = 'prod'
    dev = 'dev'
    test = 'test'


class DaprSubscribeInfoItem(BaseModel):
    """Dapr Subscribe Item"""

    pubsubname: str
    topic: str
    route: str


class TokenInfo(BaseModel):
    """Token Info

    Doc: https://datatracker.ietf.org/doc/html/rfc7519#section-4.1
    Doc: https://www.iana.org/assignments/jwt/jwt.xhtml
    """

    iss: typing.Optional[str]  # token 发布者
    sub: typing.Optional[str]  # token subject
    aud: typing.Optional[str]  # token audience 受众
    iat: typing.Optional[int]  # token 生成时间
    exp: typing.Optional[int]  # token 过期时间

    id: typing.Optional[int]  # user id
    roles: list[int] = []  # role id list


ESSearchResultSchema = create_model_from_typeddict(ESSearchResult)
