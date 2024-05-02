from rest_framework.pagination import PageNumberPagination
from recipes.constants import (
    PAGE_SIZE, MAX_PAGE_SIZE, PAGE_SIZE_QUERY_PARAM)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = PAGE_SIZE_QUERY_PARAM
    max_page_size = MAX_PAGE_SIZE
