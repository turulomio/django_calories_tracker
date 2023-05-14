from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .reusing.request_casting import RequestGetBool, RequestGetListOfBooleans, RequestGetListOfStrings

class PagePaginationWithTotalPages(PageNumberPagination):
    page_size = 10
    page_size_query_param="itemsPerPage"
    max_page_size = 30

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
    def get_index(index):
        if index<=len(sortBy)-1 and index<=len(sortDesc)-1:
            if sortDesc[index] is True:
                return f"-{sortBy[index]}"
            else:
                return sortBy[index]
        return default
    ## CHECK PARAMS in 
    sortBy=RequestGetListOfStrings(request, "sortBy[]")
    sortDesc=RequestGetListOfBooleans(request, "sortDesc[]")
    multiSort=RequestGetBool(request, "multiSort")
    if multiSort is False:
        r= [get_index(0)]
    else: #Multi sort true
        r=[]
        for i in range(len(sortDesc)):
            r.append(get_index(i))
            
    #print("vtabledata_options2orderby",  sortBy, sortDesc, multiSort, "==>",  r)
    return r
