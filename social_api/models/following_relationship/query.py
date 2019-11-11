from graphene import (
    ObjectType,
    ID,
    String,
    NonNull,
    List
)
from .model import UserFollowingType
from .import USER_FOLLOWING_RELATIONSHIP_COLLECTION
from ..user import USER_COLLECTION
from ..user.model import UserType
import logging
from ..import NUMBER_OF_RESULTS_A_TIME
from social_api import firestoreDB


class Query(ObjectType):
    user_followers = NonNull(
        List(UserType, required=False),
        toUserId=ID(required=True),
        startAfterId=ID(required=False)
    )

    shop_followers = NonNull(
        List(UserType, required=False),
        toShopId=ID(required=True),
        startAfterId=ID(required=False),
    )

    async def resolve_user_followers(self, info, **kwargs):
        """
        get followers of a single user
        """
        followers = list()
        fetchResult = None
        # check user authenticated or not
        toUserId, startAfterId = [
            kwargs.get(key, None) for key in ["toUserId", "startAfterId"]
        ]
        if toUserId and toUserId != "":
            # if has next page:
            if startAfterId and startAfterId != "":
                startAfterSnapshot = USER_FOLLOWING_RELATIONSHIP_COLLECTION.document(
                    u"{}".format(startAfterId)
                ).get()
                if startAfterSnapshot.exists:
                    try:
                        fetchResult = USER_FOLLOWING_RELATIONSHIP_COLLECTION.where(
                            u"to_user_id",
                            u"==",
                            u"{}".format(toUserId),
                        ).start_after(startAfterSnapshot).limit(NUMBER_OF_RESULTS_A_TIME).stream()
                    except Exception as e:
                        logging.error(f"Error fetching user followers: {e}")
                        pass
            # if not have start after id
            else:
                fetchResult = USER_FOLLOWING_RELATIONSHIP_COLLECTION.where(
                    u"to_user_id",
                    u"==",
                    u"{}".format(toUserId)
                ).limit(NUMBER_OF_RESULTS_A_TIME).stream()

            if not fetchResult is None:
                # create batch
                # refer to: https://firebase.google.com/docs/firestore/manage-data/transactions#batched-writes
                batch = firestoreDB.batch()
                for follower in fetchResult:
                    followerData = follower.to_dict()
                    followerData["id"] = follower.id
                    followers.append(followerData)
        return followers

    async def resolve_shop_followers(self, info, **kwargs):
        """
            get followers of single shop
        """
        toShopId, startAfterId = [
            kwargs.get(key, None) for key in ["toShopId", "startAfterId"]
        ]
        followers = list()
        fetchResult = None
        if toShopId is not None and toShopId != "":
            if startAfterId is not None and startAfterId != "":
                userFollowSnapshot = USER_FOLLOWING_RELATIONSHIP_COLLECTION.document(
                    u"{}".format(startAfterId)
                ).get()
                if userFollowSnapshot.exists:
                    try:
                        fetchResult = USER_FOLLOWING_RELATIONSHIP_COLLECTION.where(
                            u"to_shop_id",
                            u"==",
                            u"{}".format(toShopId)
                        ).start_after(userFollowSnapshot).limit(NUMBER_OF_RESULTS_A_TIME).stream()
                    except Exception as e:
                        logging.error(f"Error fetching following users: {e}")
                        pass
            else:
                try:
                    fetchResult = USER_FOLLOWING_RELATIONSHIP_COLLECTION.where(
                        u"to_shop_id",
                        u"==",
                        u"{}".format(toShopId)
                    ).limit(NUMBER_OF_RESULTS_A_TIME).stream()
                except Exception as e:
                    logging.error(f"Error fetching following users: {e}")
                    pass

            if not fetchResult is None:
                for follower in fetchResult:
                    followerData = follower.to_dict()
                    followerData["id"] = follower.id
                    followers.append(followerData)

        return followers
