from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    # تعداد رکورد در هر صفحه
    page_size = 10
    # میتونیم با این پارامتر تو query URL تغییرش بدیم
    page_size_query_param = 'page_size'
    # بیشترین تعداد رکورد در هر صفحه
    max_page_size = 100
