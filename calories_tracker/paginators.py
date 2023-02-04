from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .reusing.request_casting import RequestGetBool, RequestGetListOfBooleans, RequestGetListOfStrings

class PagePaginationWithTotalPages(PageNumberPagination):
    page_size = 10
    max_page_size = 1000000

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page': self.page.number, 
            'results': data, 
        })
        

def vtabledata_options2orderby(request, default):
    ## CHECK PARAMS in 
    sortBy=RequestGetListOfStrings(request, "sortBy[]")
    sortDesc=RequestGetListOfBooleans(request, "sortDesc[]")
    multiSort=RequestGetBool(request, "multiSort")
    print(multiSort, sortBy, sortDesc)
    if multiSort is False:
        if len(sortBy)>0:
            if sortDesc[0] is True:
                return f"-{sortBy[0]}"
            else:
                return sortBy[0]
        else:
            return default
    else:
        print("vtabledata_options2orderby Multisort Trye")
        return default
    
