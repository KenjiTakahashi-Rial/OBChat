"""
Storage for database functions that are called in multiple places and are not associated with any
particular instance of a class.
"""

def try_get(model, **kwargs):
    """
    Description:
        A safe function to attempt to retrieve a single match of a database object without raising
        an exception if it is not found.
        Does not except MultipleObjectsReturned because this function should only ever be used to
        retrieve a single match.
        For queries with multiple matches see model.objects.filter().

    Arguments:
        model (Class): A database model class (see models.py)
        kwargs: Class variable values to use for the database query

    Return values:
        A single database object whose class variable values match the kwargs, if it exists.
        Otherwise None.
    """

    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None
