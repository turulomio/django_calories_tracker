
def qs_distinct(qs,  lambda_function):
    """
        Returns a list of distinct values got from lambda_function return
    """
    s=set()
    for o in qs:
        s.add(lambda_function(o))
    return list(s)
