from graphene import List, String, ObjectType, ID, Field, NonNull, Mutation as ObjectMutation, Boolean
from .import USER_COLLECTION
from google.cloud.firestore_v1 import Increment
from .model import UserType
from ..import NUMBER_OF_RESULTS_A_TIME


class UserFollowerType(ObjectType):
    id = ID(required=False)
    user = Field(UserType, required=True)


class Query(ObjectType):
    """
    1: query all followers of a specific user
    """
    followers = NonNull(
        List(UserFollowerType, required=False),
        userId=ID(required=True, default_value=""),
        startAfterId=ID(required=False)
    )

    async def resolve_followers(self, info, **kwargs):
        user = info.context["request"].user
        followers = []
        if not user.is_authenticated:
            userId, startAfterId = [
                kwargs.get(key, None) for key in ["userId", "startAfterId"]
            ]
            if not userId is None and not startAfterId is None:
                # fetch next 10 followers after "startAfterId":
                fetchResult = USER_COLLECTION.document(u"{}".format(userId)) \
                    .collection(u"followers").start_after(
                    # get cursor document for getting result:
                    USER_COLLECTION.document(u"{}".format(userId)).collection(u"followers") \
                        .document(u"{}".format(startAfterId))
                ).limit(NUMBER_OF_RESULTS_A_TIME).stream()
                for follower in fetchResult:
                    follower = follower.to_dict()
                    dt = follower["user"].get()
                    print(dir(dt))
                # followers.append(follower.to_dict())
        return followers


class FollowUser(ObjectMutation):
    """
    1: check this user is authenticated or not.
    2: if True, then check 'userId' to follow exists or not
    3: 
    """
    ok = Boolean(required=True)
    errors = NonNull(List(String, required=False))

    class Arguments:
        userId = String(required=True)

    async def mutate(self, info, **kwargs):
        user = info.context["request"].user
        ok, errors = False, []
        if user.is_authenticated:
            userId = kwargs.get("userId", None)
            if userId:
                # get user with userId from database:
                userToFollow = USER_COLLECTION.document(
                    u"{}".format(userId)
                ).get()
                if userToFollow.exists:
                    print(dir(userToFollow))
                else:
                    errors.append("This user does not exist.")
        else:
            errors.append("Please login to follow someone.")

        return FollowUser(
            ok=ok,
            errors=errors,
        )


class Mutation(ObjectType):
    follow_user = FollowUser.Field()
