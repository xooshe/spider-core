import json
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from uuid import UUID

from django.core.exceptions import FieldDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Field, Model, Q
from django.utils.text import smart_split, unescape_string_literal
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response

from spider.api.base_api import BaseApi
from spider.dataclasses import PaginationData, PaginationRO
from spider.decorators.api_response import api_response
from spider.serializers.pagination_serializer import PaginationInfoSerializer

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

T = TypeVar("T", bound=Model)
TRoles = TypeVar("TRoles")

"""
A API View class that handle GET list and single entity queries.
"""

logger = logging.getLogger(__name__)


class ModelGetApi(BaseApi):
    model: Type[T]  # type: ignore[valid-type]
    serializer: Type[serializers.Serializer]
    search_in: Optional[Tuple[str, ...]] = None
    search_query_key: str = "s"
    filter_query_key: str = "filter_in"
    pagination: Optional[bool] = True
    filters_on: Optional[List[Tuple[str, Optional[str]]]] = None
    order_by: Optional[Tuple[str, ...]] = None
    get_roles: Tuple[TRoles, ...] = ()  # type: ignore[valid-type]
    authentication_classes: Tuple[Any, ...] = ()
    permission_classes: Tuple[Any, ...] = ()

    def get_paginate_params(
        self, request: Request
    ) -> Union[Tuple[None, None, Literal[False]], Tuple[int, int, Literal[True]]]:
        try:
            page, take = (
                int(request.query_params.get("page", [0])),
                int(request.query_params.get("take", [0])),
            )

        except Exception:
            return (None, None, False)
        return (page, take, True)

    def handle_pagination(
        self, request: Request, qs: "QuerySet[T]", page: int, take: int
    ) -> PaginationRO:
        pagination_qs = Paginator(qs, take)
        pagination_data = PaginationData()
        pagination_data.page = page
        pagination_data.take = pagination_qs.per_page
        pagination_data.total_pages = pagination_qs.num_pages
        pagination_data.total_items = pagination_qs.count

        pagination_ro = PaginationRO()
        pagination_ro.items = pagination_qs.get_page(page)
        pagination_ro.pageInfo = pagination_data

        return pagination_ro

    """
    The function `get_active_list` returns a queryset of objects that are active and meet additional
    filter criteria.
    :return: a queryset (qs) that contains all the objects from the model that have the is_active
    attribute set to True and also satisfy the additional filter conditions specified in the *args
    parameter.
    """

    def get_active_list(self, request: Request, **args: Any) -> "QuerySet[Model]":
        # Type ignore for Django's objects manager which correctly returns QuerySet[T]
        qs = self.model.objects.filter(is_active=True, **args)  # type: ignore[return-value, assignment, misc]
        return qs  # type: ignore[misc]

    def get_ordered_list(self, qs: "QuerySet[T]") -> "QuerySet[T]":
        if self.order_by:
            return qs.order_by(*self.order_by)
        return qs

    def clean_filter_fields(self) -> List[Tuple[str, str | None]]:
        clean_fields: List[Tuple[str, str | None]] = []
        if self.filters_on:
            for field in self.filters_on:
                clean_fields.append(field)
        return clean_fields

    def get_filters_term(self, request: Request) -> Dict[str, Any]:
        filter_term = request.query_params.get(self.filter_query_key, None)
        if not filter_term:
            return {}

        filter_term_obj = json.loads(filter_term)
        filter_fields = self.clean_filter_fields()

        filters: Dict[str, Any] = {}
        for field in filter_fields:
            if filter_term_obj.get(field[0]) is not None:
                if field[1] is None:
                    filters[f"__exp__{field[0]}"] = filter_term_obj.get(field[0])
                else:
                    filters[f"{field[1]}"] = filter_term_obj.get(field[0])

        return filters

    def additional_filter(
        self, qs: "QuerySet[T]", filters: Dict[str, Any]
    ) -> "QuerySet[T]":
        return qs

    def get_filtered_entities(
        self, request: Request, qs: "QuerySet[T]"
    ) -> "QuerySet[T]":
        filters: Dict[str, Any] = {}
        try:
            if self.filters_on:
                filters = self.get_filters_term(request)
                c_filters = {
                    key: filters[key] for key in filters if "__exp__" not in key
                }
                if len(c_filters):
                    qs = qs.filter(**c_filters)

            qs = self.additional_filter(qs, filters)
        except Exception:
            return qs
        return qs

    def get_one_search_query(
        self, request: Request, id_or_slug: Union[str, int]
    ) -> Model:
        raise NotImplementedError()

    def get_one(self, request: Request, **args: Any) -> Model:
        id_or_slug = args.get("id", None)
        if id_or_slug:
            try:
                try:
                    qs = self.get_one_search_query(request, id_or_slug)
                except NotImplementedError:
                    try:
                        # Type ignore for Django's get() which correctly returns T
                        qs = self.model.objects.get(Q(pk=id_or_slug))  # type: ignore[return-value, misc]
                    except ValueError:
                        qs = self.model.objects.get(Q(slug=id_or_slug))  # type: ignore[return-value, misc]
            except Exception as e:
                logger.error(e)
                # Type ignore for error handling which is handled by decorator
                return super().handle_error(  # type: ignore[return-value, misc]
                    error=f"can not resolve id {id_or_slug}",
                    code="NOT_FOUND",
                    status=404,
                )
            return qs  # type: ignore[misc]
        raise Exception("no id or slug was provided")

    @api_response
    def get(self, request: Request, **args: Any) -> Response:
        if len(self.get_roles):
            try:
                self.has_required_role(request, self.get_roles)
            except Exception as e:
                return self.handle_error(f"{e}", code="PERMISSION_ERROR", status=403)

        id_or_slug = args.get("id", None)
        if id_or_slug:
            qs = self.get_one(request, **args)
        else:
            qs = self.get_active_list(request)
            qs = self.get_ordered_list(qs)
            qs = self.get_filtered_entities(request, qs)
            search_term = request.query_params.get(self.search_query_key, None)
            if search_term:
                qs = self.get_search_results(request, qs, search_term=search_term)
            page, take, has_params = self.get_paginate_params(request)
            if (self.pagination == None and has_params) or self.pagination == True:
                if not has_params:
                    return super().handle_error(
                        error="you need to provide `page` and `take` query params in\
                                order to get paginate data",
                        code="NOT_FOUND",
                        status=404,
                    )
                if page is not None and take is not None:
                    qs = self.handle_pagination(request, qs, page, take)
        try:
            return self.success_response(qs)
        except Exception as e:
            print(e)
            return qs  # type: ignore[return-value]

    def success_response(
        self,
        data: Union[T, "QuerySet[T]", PaginationRO],
        status: Optional[int] = None,
    ) -> Response:
        if data == {}:
            return Response(status=status)
        if isinstance(data, PaginationRO):
            try:
                serialized_data = self.get_serialized_data(data.items, many=True)  # type: ignore[arg-type]
                serialized_page_data = PaginationInfoSerializer(data.pageInfo)
                return Response(
                    {
                        "items": serialized_data.data,
                        "pageInfo": serialized_page_data.data,
                    },
                    status=status,
                )
            except Exception:
                return Response(status=status or 500)
        elif hasattr(data, "__len__") and getattr(data, "__len__"):
            serialized_data = self.get_serialized_data(data, many=True)  # type: ignore[arg-type]
            return Response({"items": serialized_data.data}, status=status)
        else:
            serialized_data = self.get_serialized_data(data, many=False)
            return Response(serialized_data.data)

    def get_serialized_data(
        self, data: Union[T, "QuerySet[T]", List[T]], many: bool = True
    ) -> Union[serializers.Serializer, serializers.ListSerializer]:
        if not self.serializer:
            raise Exception("serializer is invalid")
        try:
            user = self.get_user(self.request)
        except:
            user = None
        return self.serializer(
            data,
            context={"user": user if user else None},
            many=many,
        )

    def get_search_results(
        self,
        request: Request,
        queryset: "QuerySet[T]",
        search_term: Optional[str] = None,
    ) -> "QuerySet[T]":
        def construct_search(field_name: str) -> str:
            if field_name.startswith("^"):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith("="):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith("@"):
                return "%s__search" % field_name[1:]

            opts = queryset.model._meta
            lookup_fields = field_name.split("__")
            prev_field: Optional[Field] = None

            for path_part in lookup_fields:
                if path_part == "pk":
                    path_part = opts.pk.name if opts.pk else path_part
                try:
                    field = opts.get_field(path_part)
                except FieldDoesNotExist:
                    if (
                        prev_field
                        and hasattr(prev_field, "get_lookup")
                        and prev_field.get_lookup(path_part)
                    ):
                        return field_name
                else:
                    prev_field = field
                    # Type ignore for Django's get_path_info which exists on related fields
                    if hasattr(field, "get_path_info"):  # type: ignore[attr-defined, misc]
                        opts = field.get_path_info()[-1].to_opts  # type: ignore[union-attr, misc]
            return "%s__icontains" % field_name

        search_fields = self.search_in
        if search_fields and search_term:
            orm_lookups = [
                construct_search(str(search_field)) for search_field in search_fields
            ]
            for bit in smart_split(search_term):
                if bit.startswith(('"', "'")) and bit[0] == bit[-1]:
                    bit = unescape_string_literal(bit)
                or_queries = Q(
                    *((orm_lookup, bit) for orm_lookup in orm_lookups),
                    _connector=Q.OR,
                )
                queryset = queryset.filter(or_queries)

        return queryset
