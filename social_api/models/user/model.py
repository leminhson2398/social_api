from graphene import (
    String,
    Boolean,
    ObjectType,
    Field,
    DateTime,
    Int,
)
from ..location.location import LocationType


class UserType(ObjectType):
    """
        number_of_followers will be manipulated differently.
    """
    id = String(required=False)
    first_name = String(required=False)
    last_name = String(required=False)
    username = String(required=True)
    email = String(required=True, default_value="")
    address = Field(LocationType)
    gender = String(required=True)
    date_of_birth = DateTime(required=False)
    phone_number = String(required=True, default_value="")
    active = Boolean(required=True, default_value=False)
    number_of_followers = Int(required=True, default_value=0)
