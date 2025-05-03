from collections import OrderedDict

from rest_framework.pagination import CursorPagination as DrfCursorPagination
from rest_framework.pagination import LimitOffsetPagination as DrfLimitOffsetPagination
from rest_framework.pagination import PageNumberPagination as DrfPageNumberPagination
from rest_framework.response import Response


class LimitOffsetPagination(DrfLimitOffsetPagination):
    default_limit = 10
    max_limit = 50

    def get_paginated_data(self, data):
        return OrderedDict(
            [
                ("limit", self.limit),
                ("offset", self.offset),
                ("count", self.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_paginated_response(self, data):
        """
        We redefine this method in order to return `limit` and `offset`.
        This is used by the frontend to construct the pagination itself.
        """
        return Response(
            OrderedDict(
                [
                    ("limit", self.limit),
                    ("offset", self.offset),
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )


class PageNumberPaginator(DrfPageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "size"

    def get_paginated_data(self, data):
        return OrderedDict(
            [
                ("count", self.page.paginator.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )


class CursorPaginator(DrfCursorPagination):
    cursor_query_param = "cursor"  # default
    page_size_query_param = "size"
    # default is `-created`,
    # which is not supported by our models. Ordering should be set on the view,
    #  this is a backup.
    ordering = "-created_at"

    def get_paginated_data(self, data):
        return OrderedDict(
            [
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_paginated_response(self, data):
        return Response(self.get_paginated_data(data))
