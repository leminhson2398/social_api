from graphene import (
    ObjectType,
    ID,
    String,
    NonNull,
    List
)
from .import USER_FOLLOWING_RELATIONSHIP_COLLECTION
from ..user import USER_COLLECTION
from ..user.model import UserType
import logging
from ..import NUMBER_OF_RESULTS_A_TIME
from social_api import firestoreDB
import typing
from google.cloud.firestore_v1 import DocumentSnapshot, DocumentReference


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
        followers: typing.List[dict] = list()
        followShipGenerator: typing.Any = None

        toUserId: str = kwargs.get("toUserId", "")
        startAfterId: str = kwargs.get("startAfterId", "")

        if toUserId != "":
            # get document reference for 'to_user'
            toUserDocRef: DocumentReference = USER_COLLECTION.document(
                u"{}".format(toUserId))
            # if has next page:
            if startAfterId != "":
                # get cursor document snapshot:
                startAfterSnapshot: DocumentSnapshot = USER_FOLLOWING_RELATIONSHIP_COLLECTION.document(
                    u"{}".format(startAfterId)).get()
                # check existance of cursor snapshot
                if startAfterSnapshot.exists:
                    try:
                        followShipGenerator = USER_FOLLOWING_RELATIONSHIP_COLLECTION.where(
                            u"to_user",
                            u"==",
                            u"{}".format(toUserDocRef)
                        ).start_after(startAfterSnapshot).limit(NUMBER_OF_RESULTS_A_TIME).stream()
                    except Exception as e:
                        logging.error(f"Error fetching user followers: {e}.")
            # if not have start after id
            else:
                followShipGenerator = USER_FOLLOWING_RELATIONSHIP_COLLECTION.where(
                    u"to_user",
                    u"==",
                    u"{}".format(toUserDocRef)
                ).limit(NUMBER_OF_RESULTS_A_TIME).stream()

            if not followShipGenerator is None:
                for followShip in followShipGenerator:
                    follower: DocumentReference = followShip.to_dict().get(u"from_user", None)
                    followers.append(follower.get())
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
