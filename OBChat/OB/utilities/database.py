"""
Storage for database functions that are called in multiple places and are not associated with any
particular instance of a class.
"""

from channels.db import database_sync_to_async

from OB.models import OBUser

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
    """

    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

@database_sync_to_async
def async_try_get(model, **kwargs):
    """
    Description:
        Allows an asynchronous function to safely retreive a single database object.

    Arguments:
        model (Class): A database model class (see OB.models.py).
        kwargs: Class variable values to use for the database query.

    Return values:
        A single database object whose class variable values match the kwargs, if it exists.
    """

    return try_get(model, **kwargs)

@database_sync_to_async
def async_get(model, **kwargs):
    """
    Description:
        Allows an asynchronous function to retreive a single database object.

    Arguments:
        model (Class): A database model class (see OB.models.py).
        kwargs: Class variable values to use for the database query.

    Return values:
        A single database object whose class variable values match the kwargs
    """

    return model.objects.get(**kwargs)

@database_sync_to_async
def async_save(model_or_object, **kwargs):
    """
    Description:
        Allows an asynchronous function to save a new database object.

    Arguments:
        model_or_object: A database model class or a database object (see OB.models.py).
            If there are no kwargs, then it is assumed that this is an object, not a model.
        kwargs: Class variable values to assign to the new database object.

    Return values:
        The newly created database object or the existing database object that was just saved.
    """

    if not kwargs:
        model_or_object.save()
        return model_or_object

    if model_or_object is OBUser:
        new_object = OBUser.objects.create_user(**kwargs)
    else:
        new_object = model_or_object(**kwargs)

    new_object.save()
    return new_object

@database_sync_to_async
def async_delete(delete_object):
    """
    Description:
        Allows an asynchronous function to delete a database object.

    Arguments:
        delete_object: The database object to delete.
    """

    delete_object.delete()


@database_sync_to_async
def async_add(field, add_object):
    """
    Description:
        Allows an asynchronous function to add to a database object's OneToManyField or
        ManyToManyField.

    Arguments:
        field (OneToManyField/ManyToManyField): A database object's field to add to.
        add_object: The database object to add. Type must match to object model's type (see
            OB.models.py).
    """

    field.add(add_object)

@database_sync_to_async
def async_remove(field, remove_object):
    """
    Description:
        Allows an asynchronous function to remove from a database object's OneToManyField or
        ManyToManyField.

    Arguments:
        field (OneToManyField/ManyToManyField): A database object's field to remove from.
        remove_object: The database object to remove. Type must match to object model's type (see
            OB.models.py).
    """

    field.remove(remove_object)

@database_sync_to_async
def async_len_all(query_set):
    """
    Description:
        Allows an asynchronous function to get the length of a database table.

    Arguments:
        table: A database table to find the length of.
               May be in the form QuerySet, OneToManyField, ManyToManyField, etc., as long as there
               exists a corresponding table in the database.

    Return values:
        The integer value of the length of the table.
    """

    return len(query_set.all())

@database_sync_to_async
def async_model_list(model):
    """
    Description:
        Allows an asynchronous function to get a list of database objects of a model so that it
        may be iterated on asynchronously.

    Arguments:
        model: The model to get a list of.
            May also be a ManyRelatedManager, which has its own table in the database.

    Return values:
        A list of database objects from the model's QuerySet.
    """

    # pylint: disable=unnecessary-comprehension
    # Justification: These comprehensions are necessary to make a list of database objects. If
    #   [model.objects.all()] is used, the list will contain QuerySets, not database objects.
    try:
        return [user for user in model.objects.all()]
    except AttributeError:
        # ManyRelatedManager types do not have an objects attribute
        return [user for user in model.all()]

@database_sync_to_async
def async_get_owner(room):
    """
    Description:
        Allows an asynchronous function to get the owner attribute of a Room.
        The owner attribute of a Room is a ForeignKey, which require a database query to access.
    Arguments:
        room (Room): The Room object to get the owner attribute of.

    Return values:
        The OBUser owner attribute of the room argument.
    """

    return room.owner

def add_occupants(room, occupants):
    """
    Description:
        Adds a list of users to the occupants of room if they are not already in it.

    Arguments:
        room (Room): The room to add users to the occupants of.
        occupants (list[OBUser]): The list of users to add to the room's occupants list.
    """

    for user in occupants:
        if user not in room.occupants.all():
            room.occupants.add(user)

@database_sync_to_async
def async_add_occupants(room, occupants):
    """
    Description:
        Allows an asynchronous function to add a list of users to the occupants of room if they are
        not already in it.

    Arguments:
        room (Room): The room to add users to the occupants of.
        occupants (list[OBUser]): The list of users to add to the room's occupants list.
    """

    add_occupants(room, occupants)
