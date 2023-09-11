
def qs_distinct(qs,  lambda_function):
    """
        Returns a list of distinct values got from lambda_function return
    """
    s=set()
    for o in qs:
        s.add(lambda_function(o))
    return list(s)

def qs_dict(qs, lambda_function):
    """
        Returns a dict generated from qs, where keys is the result of the lambda_function
    """
    d={}
    for o in qs:
        d[lambda_function(o)]=o
    return d
