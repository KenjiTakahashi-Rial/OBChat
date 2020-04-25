"""
Storage for database functions that are called in multiple places and are not associated with any
particular instance of a class.
"""

from channels.db import database_sync_to_async

from OB.models import Admin, OBUser

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
def sync_try_get(model, **kwargs):
    """
    Description:
        Allows an asynchronous function to safely retreive a single database object.

    Arguments:
        model (Class): A database model class (see OB.models.py).
        kwargs: Class variable values to use for the database query.

    Return values:
        A single database object whose class variable values match the kwargs, if it exists.
        Otherwise None.
    """

    return try_get(model, **kwargs)

@database_sync_to_async
def sync_get(model, **kwargs):
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

    if model is OBUser:
        new_database_object = OBUser.objects.create_user(**kwargs)
    else:
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

@database_sync_to_async
def sync_len_all(table):
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

    return len(table.all())

@database_sync_to_async
def sync_get_occupants(room):
    """
    Description:
        Allows an asynchronous function to get the occupants of a room as a list of OBUser objects.

    Arguments:
        room (Room): The room to get the occupant name list of.

    Return values:
        A list of OBUser objects who are occupying the room.
    """

    # pylint: disable=unnecessary-comprehension
    # This comprehension is necessary because [room.occupants.all()] returns a list of 1 QuerySet
    return [user for user in room.occupants.all()]

@database_sync_to_async
def sync_equals(object_a, object_b):
    """
    Description:
        Allows an asynchronous function to compare database objects.

    Arguments:
        object_a (database object): The first object to compare.
        object_b (database object): The second object to compare.

    Return values:
        A boolean indicating if the two objects are equal.
    """

    return object_a == object_b

@database_sync_to_async
def sync_get_who_string(user, room):
    """
    Description:
        Allows an asynchronous function to compare database objects.

    Arguments:
        object_a (database object): The first object to compare.
        object_b (database object): The second object to compare.

    Return values:
        A boolean indicating if the two objects are equal.
    """

    who_string = f"Chatters in: {room.display_name} ({room.name})\n"

    for occupant in room.occupants.all():
        occupant_string = f"{occupant.display_name} ({occupant.username})"

        # Tag occupant appropriately
        if occupant == room.owner:
            occupant_string += " [owner]"
        if try_get(Admin, user=occupant, room=room):
            occupant_string += " [admin]"
        if occupant == user:
            occupant_string += " [you]"

        who_string += occupant_string + "\n"

    return who_string
