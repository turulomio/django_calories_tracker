
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

def string2list_of_integers(s, separator=", "):
    """Convers a string of integer separated by comma, into a list of integer"""
    arr=[]
    if s!="":
        arrs=s.split(separator)
        for a in arrs:
            arr.append(int(a))
    return arr
