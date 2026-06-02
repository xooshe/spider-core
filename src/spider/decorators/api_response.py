import functools
from rest_framework.response import Response

from spider.exeptions.base_api_exeption import BaseApiException


def api_response(view_func):
    """
    A decorator for formatting API responses.

    This decorator is used to format the API responses by wrapping the
    response data in the desired format: {"data": response.data, "error": None}.
    It also handles exceptions of type `BaseApiException` and returns
    error responses with the specified error detail and status code.

    Args:
        view_func (function): The view function to decorate.

    Returns:
        function: The decorated view function.

    Example:
        @api_response
        def your_api_view(request):
            # Your view logic here
            data = {"message": "Success!"}
            return Response(data, status=200)
    """

    @functools.wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            response = view_func(request, *args, **kwargs)
            # Check if the response is a Response object
            if isinstance(response, Response):
                response.data = {"data": response.data, "error": None}
            return response
        except BaseApiException as e:
            return Response({"data": None, "error": e.detail}, status=e.status_code)

    return _wrapped_view
