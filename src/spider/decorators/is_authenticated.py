import functools
from spider.exeptions.base_api_exeption import BaseApiException


def is_authenticated(view_method):
    """
    Custom decorator to check if the user is authenticated.
    """

    @functools.wraps(view_method)
    def _wrapped_view(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # User is authenticated, allow access to the view
            return view_method(self, request, *args, **kwargs)
        else:
            # User is not authenticated, return a 403 Forbidden response
            raise BaseApiException(
                401,
                {"message": "authentication needed", "code": "AUTHENTICATION_NEEDED"},
            )

    return _wrapped_view
