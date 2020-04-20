"""
Storage for database functions that are called in multiple places and are not associated with any
particular instance of a class.
"""

from channels.db import database_sync_to_async

def try_get(model, **kwargs):
    """
    Description:
        A safe function to attempt to retrieve a single match of a database object without raising
        an exception if it is not found.
        Does not except MultipleObjectsReturned because this function should only ever be used to
        retrieve a single match.
        For queries with multiple matches see model.objects.filter().

    Arguments:
        model (Class): A database model class (see OB.models.py).
        kwargs: Class variable values to use for the database query.

    Return values:
        A single database object whose class variable values match the kwargs, if it exists.
        Otherwise None.
    """

    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

@database_sync_to_async
def sync_get(model, **kwargs):
    """
    Description:
        Allows an asynchronous function to retreive a single database object.

    Arguments:
        model (Class): A database model class (see OB.models.py).
        kwargs: Class variable values to use for the database query.

    Return values:
        A single database object whose class variable values match the kwargs, if it exists.
        Otherwise None.
    """

    return model.objects.get(**kwargs)

@database_sync_to_async
def sync_save(model, **kwargs):
    """
    Description:
        Allows an asynchronous function to save a new database object.

    Arguments:
        model (Class): A database model class (see OB.models.py).
        kwargs: Class variable values to assign to the new database object.

    Return values:
        The newly created database object.
    """

    new_database_object = model(**kwargs)
    new_database_object.save()
    return new_database_object

@database_sync_to_async
def sync_delete(delete_object):
    """
    Description:
        Allows an asynchronous function to delete a database object.

    Arguments:
        delete_object: The database object to delete.

    Return values:
        None.
    """

    delete_object.delete()


@database_sync_to_async
def sync_add(field, add_object):
    """
    Description:
        Allows an asynchronous function to add to a database object's OneToManyField or
        ManyToManyField.

    Arguments:
        field (OneToManyField/ManyToManyField): A database object's field to add to.
        add_object: The database object to add. Type must match to object model's type (see
            OB.models.py).

    Return values:
        None.
    """

    field.add(add_object)

@database_sync_to_async
def sync_remove(field, remove_object):
    """
    Description:
        Allows an asynchronous function to remove from a database object's OneToManyField or
        ManyToManyField.

    Arguments:
        field (OneToManyField/ManyToManyField): A database object's field to remove from.
        remove_object: The database object to remove. Type must match to object model's type (see
            OB.models.py).

    Return values:
        None.
    """

    field.remove(remove_object)
