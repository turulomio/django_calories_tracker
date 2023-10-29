from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .reusing.request_casting import RequestGetBool

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
    def vuetify_sortby2lod(request):
        """
            Creates a dictionary from vuetify v-data-table-server request
        """
        i=0
        r=[]
        while True:
            if f"sortBy[{i}][key]" in request.GET:
                r.append({"key": request.GET[f"sortBy[{i}][key]"], "order": request.GET[f"sortBy[{i}][order]"]})                
            else:
                break
            i+=1
        return r
    def lod2django(lod):
        """
            Retuurns a list with all order django strings from vuetify_sortby2lod
        """
        r=[]
        for d in lod:
            if d["order"]=="asc":
                r.append(d["key"])
            else:
                r.append(f"-{d['key']}")
        return r
    ## CHECK PARAMS in 
    lod=vuetify_sortby2lod(request)
    multiSort=RequestGetBool(request, "multiSort")
    if len(lod)==0: #Devuelve default, paginate siempre tiene que estar ordenado
        return [default]
        
    django_sorts=lod2django(lod)
    if multiSort is False:
        r= [django_sorts[0]]
    else: #Multi sort true
        r=django_sorts
    
    #print("vtabledata_options2orderby",  sortBy, sortDesc, multiSort, "==>",  r)
    return r
