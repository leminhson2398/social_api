from graphene import ObjectType, ID

from ..user.model import UserType


class UserFollowingType(ObjectType):
    id          = ID(required=False)
    to_user     = UserType(required=True)
    from_user   = UserType(required=True)
