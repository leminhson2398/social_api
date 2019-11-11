from graphene import ObjectType, ID, String, DateTime, Field, Boolean, Decimal
from ..location.location import LocationType


class OrderType(ObjectType):
    id = ID(required=True)
    user_email = String(required=True)
    address = Field(LocationType, required=True)
    postal_code = String(required=True)
    paid = Boolean(required=True, default_value=False)
    discount = Decimal(required=True, default_value=0)
