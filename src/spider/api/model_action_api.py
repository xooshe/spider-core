"""
A generic API view for handling CRUD operations (Create, Update and Delete) on a Django model.

Attributes:
    model (Type[Model]): The Django model associated with the API view.
    serializer (Type[serializers.Serializer]): The serializer class for serializing and deserializing model instances.
    input (Optional[List[Tuple]]): An array of tuples providing input fields for creating and updating objects.
                                     Each tuple should provide the following fields: field, field_type, *options.
                                     Options include nullable, ... (to be continued).
    action_roles (Tuple): A tuple of roles required to perform actions on the model.

Methods:
    clean_input: Clean and validate input data based on the specified input fields.
    get_instance: Create a new model instance based on the cleaned input data.
    post: Handle the HTTP POST request for creating objects.
    clear_old_instance: Clear old instance data, preserving created_at if available.
    put: Handle the HTTP PUT request for updating objects.
    on_update_full_clean: Perform full_clean during object update.
    on_create_full_clean: Perform full_clean during object creation.
    delete: Handle the HTTP DELETE request for deleting objects.
    success_response: Build a success response with serialized data.
    get_serialized_data: Get the serialized data using the specified serializer.

Example Usage:
    class MyModelActionApi(ModelActionApi):
        model = MyModel
        serializer = MyModelSerializer
        input = [('name', str, 'nullable'), ('quantity', int)]
        action_roles = ('admin', 'editor')
"""

from typing import Any, List, Optional, Tuple, Type, TypeVar

from django.db import IntegrityError
from django.db.models.base import Model
from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response

from spider.api.base_api import BaseApi
from spider.decorators.api_response import api_response
from spider.exeptions import BaseApiException

ModelType = TypeVar("ModelType")


class ModelActionApi(BaseApi):
    model: Type[Model]
    serializer = None
    """input is an Array of tuples that provide input field for create and update objects.
    each Tuple of this Array should provide this fields: field, field_type, *options
    options are nullable, model_bypass, ...FINISH_LATER
    """
    input: Optional[List[Tuple]] = None
    action_roles = ()

    def clean_input(self, input, request):
        """
        Clean and validate input data based on the specified input fields.
        initially use for input validation.

        Args:
            input (dict): Input data received in the request.
            request (HttpRequest): The HTTP request object.

        Returns:
            List[Tuple]: A list of cleaned input fields as tuples.

        Raises:
            BaseApiException: If input validation fails.
        """
        clean_input: List[Tuple] = []
        if self.input:
            for field, field_type, *options in self.input:
                if "bypass_model" in options or hasattr(self.model, field):
                    field_value = input.get(field)
                    # boolean parser
                    if field_type == bool and field_value:
                        field_value = (
                            True
                            if field_value == "true" or field_value == True
                            else False
                        )
                    if field_type == float and field_value:
                        field_value = float(field_value)
                    if (field_value is None and "nullable" not in options) or (
                        field_value != None
                        and (
                            field_type != "any" and field_type is not type(field_value)
                        )
                    ):
                        if type(field_type) != str:
                            field_type_name = field_type.__name__
                        else:
                            field_type_name = field_type
                        raise BaseApiException(
                            400,
                            f"expected value of type {field_type_name} for field: {field}. {field_value} with type {type(field_value).__name__} was provided!",
                        )
                    if field_value != None:
                        clean_input.append((field, field_value))

        return clean_input

    def get_instance(
        self, clean_input, instance: Type["Model"] | dict[Any, Any]
    ) -> "type[Model]":
        new_instance = {}
        if instance:
            new_instance: Any = instance
        for field in clean_input:
            field_name, field_value = field
            new_instance[field_name] = field_value
        return self.model(**new_instance)  # type: ignore

    def check_role(self, request):
        """
        Checks if the request has the required role permissions for the specified action roles.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response | None: If the user doesn't have the required role, returns an error response.
                             Otherwise, returns None.
        """
        try:
            self.has_required_role(request, self.action_roles)
        except Exception as e:
            return self.handle_error(f"{e}", code="PERMISSION_ERROR", status=403)

    def clean_input_object(self, request):
        """
        Cleans and validates the input data received in the request.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            List[Tuple] | Response: If input cleaning fails, returns an error response.
                                    Otherwise, returns the cleaned input data as a list of tuples.
        """
        input = request.data
        try:
            clean_input = self.clean_input(input, request)
        except Exception as e:
            return self.handle_error(
                f"{e}",
                "FIELD_TYPE",
                status=400,
            )
        return clean_input

    @api_response
    def post(self, request):
        """
        Handle the HTTP POST request for creating objects.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response.

        Raises:
            ... (exceptions and implementation details)
        """
        self.check_role(request=request)
        clean_input = self.clean_input_object(request)

        try:
            instance = self.get_instance(clean_input, {})
            if self.validate_owner(request, instance):
                try:
                    self.on_create_full_clean(instance=instance)
                except ValidationError as e:
                    return self.handle_error(
                        str(e), code="VALIDATION_ERROR", status=400
                    )
                instance.save()  # type: ignore
            else:
                return self.handle_error(
                    "validation owner not passed!",
                    code="OWNER_ERROR",
                    status=400,
                )
        except IntegrityError as e:
            return self.handle_error(f"{e}", code="ERROR_IN_SAVE", status=400)
        return self.success_response(instance)

    def clear_old_instance(self, instance, dict_instance):
        """
        Clear old instance data, preserving created_at if available.

        Args:
            instance (Type[Model]): The existing model instance.
            dict_instance (dict): Dictionary representation of the existing instance.

        Returns:
            dict: The cleared dictionary instance.
        """
        if hasattr(instance, "created_at"):
            dict_instance["created_at"] = instance.created_at
        return dict_instance

    @api_response
    def put(self, request, id):
        """
        Handle the HTTP PUT request for updating objects.

        Args:
            request (HttpRequest): The HTTP request object.
            id (int): The ID of the object to be updated.

        Returns:
            Response: The HTTP response.

        Raises:
            ... (exceptions and implementation details)
        """
        try:
            self.has_required_role(request, self.action_roles)
        except Exception as e:
            return self.handle_error(
                f"{e}", code="PERMISSION_ERROR", status=status.HTTP_403_FORBIDDEN
            )
        try:
            instance = self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return self.handle_error(
                f"could not resolve instance with id: {id}",
                code="NOT_FOUND",
                status=404,
            )

        input = request.data
        try:
            clean_input = self.clean_input(input, request)
        except Exception as e:
            return self.handle_error(
                f"{e}",
                "FIELD_TYPE",
                status=400,
            )

        if self.validate_owner(request, instance):
            try:
                # Update the instance with new values
                for field_name, field_value in clean_input:
                    setattr(instance, field_name, field_value)

                self.on_update_full_clean(instance=instance)
                instance.save()
            except ValidationError as e:
                return self.handle_error(str(e), code="VALIDATION_ERROR", status=400)
        else:
            return self.handle_error(
                "validation owner not passed!",
                code="OWNER_ERROR",
                status=400,
            )

        return self.success_response(instance)

    def on_update_full_clean(self, instance, exclude=["id"]):
        """
        Perform full_clean during object update.

        Args:
            instance (Type[Model]): The model instance.
            exclude (List[str]): List of fields to exclude during full_clean.

        Returns:
            ... (return type and implementation details)
        """
        return instance.full_clean(exclude=exclude)

    def on_create_full_clean(self, instance, exclude=[]):
        """
        Perform full_clean during object creation.

        Args:
            instance (Type[Model]): The model instance.
            exclude (List[str]): List of fields to exclude during full_clean.

        Returns:
            ... (return type and implementation details)
        """
        return instance.full_clean(exclude=exclude)

    @api_response
    def delete(self, request, id):
        """
        Handle the HTTP DELETE request for deleting objects.

        Args:
            request (HttpRequest): The HTTP request object.
            id (int): The ID of the object to be deleted.

        Returns:
            Response: The HTTP response.

        Raises:
            ... (exceptions and implementation details)
        """
        try:
            instance = self.model.objects.get(pk=id)
        except:
            return self.handle_error(
                "object does not exists",
                code="DOES_NOT_EXISTS",
                status=404,
            )
        try:
            self.has_required_role(request, self.action_roles)
        except Exception as e:
            return self.handle_error(
                f"{e}", code="PERMISSION_ERROR", status=status.HTTP_403_FORBIDDEN
            )

        try:
            if self.validate_owner(request, instance):
                instance.delete()
            else:
                return self.handle_error(
                    "validation owner not passed!",
                    code="OWNER_ERROR",
                    status=400,
                )
        except Exception as e:
            return self.handle_error(f"{e}", code="ERROR_IN_DELETE", status=400)
        return Response(
            data={"data": "delete was successful", "code": "OBJECT_DELETED"},
            status=status.HTTP_204_NO_CONTENT,
        )

    def success_response(self, data):
        """
        Build a success response with serialized data.

        Args:
            data (Any): The data to be serialized and included in the response.

        Returns:
            Response: The HTTP response.
        """
        # check if queryset is an array or not.
        if hasattr(data, "__len__"):
            serialized_data = self.get_serialized_data(data, many=True)
        else:
            serialized_data = self.get_serialized_data(data, many=False)

        return Response({"data": serialized_data.data})

    def get_serialized_data(self, data, many=True):
        """
        Get the serialized data using the specified serializer.

        Args:
            data (Any): The data to be serialized.
            many (bool): Whether to serialize as a list or a single instance.

        Returns:
            serializers.Serializer: The serialized data.
        """
        if not self.serializer:
            raise Exception("serializer is invalid")

        return self.serializer(data, many=many)
