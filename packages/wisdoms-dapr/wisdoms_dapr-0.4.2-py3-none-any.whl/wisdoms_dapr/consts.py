"""Share Constants"""

# ******* Consts *******
DEFAULT_APPID = "default"
DEFAULT_PUBSUB_NAME = "pubsub"

# ******* Env Names *******
ENV_NAME_DAPR_APP_ID = 'APP_ID'
ENV_NAME_SERVICE_RUN_MODE = 'SERVICE_RUN_MODE'
ENV_NAME_SERVICE_VERSION = 'SERVICE_VERSION'

# ******* Route Tag Names *******
ROUTE_TAG_NAME_AUTO_REGISTER = 'Auto Register'

# ******* Share Event Topic Names *******
EVENT_TOPIC_NAME_SERVICE_REGISTER = 'service_register'
EVENT_TOPIC_NAME_SCHEDULE_TASK_REGISTER = 'schedule_task_register'

# ******* Share Event Subscribe Route Names *******
EVENT_SUBSCRIBE_ROUTE_SERVICE_REGISTER = 'subscribe_service_register'
EVENT_SUBSCRIBE_ROUTE_SCHEDULE_TASK_REGISTER = (
    'subscribe_schedule_task_register'
)

# ******* Service Share Invoke Route Names *******
INVOKE_ROUTE_POLICY_SERVICE_SCHEDULE_TASK_REGISTER = 'v1/register/service'

# ******* Content Types *******
CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_TEXT = 'text/plain'

# ******* HTTP Verbs *******
HTTP_VERB_GET = 'GET'
HTTP_VERB_POST = 'POST'
HTTP_VERB_DELETE = 'DELETE'
HTTP_VERB_PUT = 'PUT'
HTTP_VERB_PATCH = 'PATCH'
HTTP_VERB_OPTION = 'OPTION'
HTTP_VERB_HEAD = 'HEAD'

# ******* Service Names *******
SERVICE_NAME_POLICY = 'policy'

# ******* Share Header Names *******
HEADER_NAME_APPID = 'x-appid'
HEADER_NAME_TOKEN = 'x-token'
HEADER_NAME_CALL_VIA = 'x-call-via'

# ******* Enforce Request Forward Header Names *******
ENFORCE_REQUEST_FORWARD_HEADER_NAME_URL = 'x-forward-url'
ENFORCE_REQUEST_FORWARD_HEADER_NAME_VERB = 'x-forward-verb'
ENFORCE_REQUEST_FORWARD_HEADER_NAME_SERVICE_NAME = 'x-forward-service-name'
ENFORCE_REQUEST_FORWARD_HEADER_NAME_SERVICE_VERSION = (
    'x-forward-service-version'
)
ENFORCE_REQUEST_FORWARD_HEADER_NAME_SERVICE_RUN_MODE = 'x-forward-service-mode'
ENFORCE_REQUEST_FORWARD_WHITELIST_URL_PATH: list[str] = [
    # Dapr Routes
    '/dapr/config',
    '/dapr/subscribe',
    # Special Register Event Routes
    '/' + EVENT_SUBSCRIBE_ROUTE_SERVICE_REGISTER,
    '/' + EVENT_SUBSCRIBE_ROUTE_SCHEDULE_TASK_REGISTER,
]
ENFORCE_REQUEST_FORWARD_WHITELIST_VERB: list[str] = [HTTP_VERB_OPTION]
