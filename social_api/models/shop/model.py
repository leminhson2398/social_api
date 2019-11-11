from graphene import ObjectType, String, List, ID, Int, Field, Boolean
from ..location.location import LocationType
from ..user.model import UserType


class ShopType(ObjectType):
    id = ID(required=True)
    name = String(required=True)
    address = Field(LocationType, required=True)
    owner = Field(UserType, required=True)
    email = String(required=True)
    phone_number = String(required=True)
    slogan = String(required=True)
    # categories can only has at most 3 items
    categories = List(String, required=True)
    avatar = String(required=True)
    views = Int(required=True, default_value=0)
    active = Boolean(required=True, default_value=False)
    number_of_followers = Int(required=True, default_value=0)
