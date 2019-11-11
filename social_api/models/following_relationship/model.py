from graphene import (
    Int,
    ID,
    ObjectType,
    Field
)
from ..user.model import UserType


class UserFollowingType(ObjectType):
    id = ID(required=False)
    to_user_id = ID(required=True)
    from_user_id = ID(required=True)
