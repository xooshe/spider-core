from rest_framework.response import Response
from spider.api.model_action_api import ModelActionApi


class MediaApi(ModelActionApi):
    """MediaApi is an abstract class for crud Objects Media related model.
        it takes
    Args:
        BaseApi (_type_): _description_
    """

    model = None
    media_field: "str" = "image"
    media_serializer = None
    media_related_id_field: "str"
    media_related_model = None

    # input =
    def post(self, request, **kwargs):
        try:
            self.has_required_role(request, self.action_roles)
        except Exception as e:
            return self.handle_error(f"{e}", code="PERMISSION_ERROR", status=403)

        input = request.data
        try:
            related_obj = self.media_related_model.objects.get(
                id=input[self.media_related_id_field]
            )
        except:
            return self.handle_error(
                error=f"expected field {self.media_related_id_field} to provide instance of {self.media_related_model._meta}.",
                code="error_media_add",
                status=404,
            )

        if input.get(self.media_field, None):
            serialized_media = self.media_serializer(data=input)
            if serialized_media.is_valid():
                media = serialized_media.save()
                related_obj.media.add(media)
                related_obj.save()
                return Response({"data": serialized_media.data})
            return self.handle_error(
                error=serialized_media.errors,
                code="error_media_add",
                status=400,
            )

        else:
            return self.handle_error(
                error=f"expected field {self.media_field} to provide media file.",
                code="no_valid_file",
                status=400,
            )

    def delete(self, request, id):
        try:
            self.has_required_role(request, self.action_roles)
        except Exception as e:
            return self.handle_error(f"{e}", code="PERMISSION_ERROR", status=403)
        try:
            media = self.model.objects.get(id=id)
        except:
            return self.handle_error(
                error="not found media",
                status=404,
                code="not_found_media",
            )
        if self.validate_owner(request, media):
            media.delete()
            return Response({"data": "successfully deleted"})
        else:
            return self.handle_error(
                "validation owner not passed!",
                code="OWNER_ERROR",
                status=400,
            )
