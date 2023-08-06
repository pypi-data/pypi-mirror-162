import logging

from rest_framework.exceptions import NotAuthenticated
from rest_framework.views import exception_handler

from .exceptions import UnprocessableEntityError
from .serializers.utils import DetailedValidationErrorInfo

logger = logging.getLogger(__name__)
exceptions_to_info = (
    NotAuthenticated,
    UnprocessableEntityError,
    DetailedValidationErrorInfo,
)


def exception_logger(exception: Exception, _):
    """Logs given exception (because it is not done by default handler)."""
    if exception and isinstance(exception, exceptions_to_info):
        # user is not logged in
        # or entered wrong data which has been detected
        logger.info(exception)
    else:
        logger.error(exception)
    return exception_handler(exception, _)
