from typing import TYPE_CHECKING, Optional, Type

from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from spider.exeptions.base_api_exeption import BaseApiException

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser as User


class BaseApi(APIView):
    """Base Api class. handle base methods for all type of request."""

    def handle_error(self, error: str, code: str, status: int):
        """return an Error Response object base of Args.

        Args:
            error (any): it returns as message. could be a object of\
                  errors returned by serializers or just a string explaining the\
                  error that happend.
            code (number): error code that returns with error object.
            status (status): status of error.

        """
        raise BaseApiException(status, error)

    def has_required_role(self, request, roles):
        """
        Args:
            request (_type_): rest_framework request
        Returns:
            Exception("permission error!"): when user doesn't have right roles to do this action..
            Exception("role is required!"): when user doesn't have any roles.
        """
        user = self.get_user(request)
        if hasattr(user, "role"):
            if roles and len(roles) and user and user.role not in roles:
                raise Exception("permission error!")
        else:
            raise Exception("role is required!")

    def get_error_obj(self, error, code, status):
        return {"error": {"message": error, "code": code}}

    def get_user(self, request) -> Type["User"] | None:
        if request.user and request.user.id:
            return request.user
        #     return request.user
        jWTAuthentication = JWTAuthentication()
        token = jWTAuthentication.get_header(request)
        if token is None:
            return None

        raw_token: Optional[str] = None

        if raw_token_exists := jWTAuthentication.get_raw_token(token):
            raw_token = str(raw_token_exists.decode())

        if raw_token and raw_token != "None":
            validated_token = jWTAuthentication.get_validated_token(raw_token)
            user = jWTAuthentication.get_user(validated_token)

            return user
        return None

    def full_clean(self, instance, exclude=[]):
        return instance.full_clean(exclude=exclude)

    def validate_owner(self, request, obj):
        """rewrite this method in child class to check owner of entity that going to change in actions.

        Args:
            request (_type_): rest_framework request
            obj (_type_): instance of initial Model

        Returns:
            True: if user is the owner of this object
            False: if user is not the owner of this object.
        Example:
            return obj.owner == self.get_user(request)

        """
        return True
