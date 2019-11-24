from graphene import ObjectType, Mutation as ObjectMutation, Boolean, List, String, ID
from .import USER_FOLLOWING_RELATIONSHIP_COLLECTION
import logging
from ..utils.utils import increase_or_decrease_a_document_field, remove_documents_from_a_collection
from ..user import USER_COLLECTION
from ..shop import SHOP_COLLECTION


class ToggleFollowUser(ObjectMutation):
    ok = Boolean(required=True)
    errors = List(String, required=False)

    class Arguments:
        toUserId = ID(required=True)

    async def mutate(self, info, **kwargs):
        """
        finding follow relation ship based on "toUserId" the user provides
        if the relationship does exist: remove it
        else: add it
        """
        ok, errors = False, list()
        user = info.context["request"].user
        followingRelationshipToRemove = None
        toUserId: str = kwargs.get("toUserId", "")
        # check authenticated or not
        if user.is_authenticated:
            # get the request user id:
            # attribute "id" of user object comes from authentication middleware
            myUserId = getattr(user, "id", None)
            if not myUserId is None and myUserId != "":
                if toUserId and toUserId != "":
                    # check whether following relation ship exists or not:
                    try:
                        followingShipGenerator = USER_FOLLOWING_RELATIONSHIP_COLLECTION.where(
                            u"to_user_id",
                            u"==",
                            u"{}".format(toUserId)
                        ).where(
                            u"from_user_id",
                            u"==",
                            u"{}".format(myUserId)
                        ).stream()
                    except Exception as e:
                        logging.error(f"Error fetching following ship: {e}")
                        pass
                    else:
                        followingShips = [
                            followShip for followShip in followingShipGenerator
                        ]
                        # check are there any following ship or not:
                        if len(followingShips):
                            followingRelationshipToRemove = followingShips
                            # indicate success
                            ok = True
                        else:
                            try:
                                USER_FOLLOWING_RELATIONSHIP_COLLECTION.add({
                                    u"from_user_id": myUserId,
                                    u"to_user_id": toUserId,
                                })
                            except Exception as e:
                                logging.error(f"Error following \
                                    this user: {e}.")
                                errors.append("Error following this user.")
                                pass
                            else:
                                # indicate success
                                ok = True
                else:
                    errors.append("You need to provide an id.")
            else:
                pass
        else:
            errors.append("You have to login to follow people.")

        # add background tasks:
        if ok:
            background = info.context["background"]
            amount = len(followingRelationshipToRemove)
            # if "removeFollowingRelationShips" is not empty, remove all the existing following relation ship:
            if isinstance(followingRelationshipToRemove, list) and amount > 0:
                background.add_task(
                    remove_documents_from_a_collection,
                    followingRelationshipToRemove
                )
            # IMPORTANT: increase 1 or decrease abitrary to number of followers of the person:
            background.add_task(
                increase_or_decrease_a_document_field,
                USER_COLLECTION,
                toUserId,
                u"number_of_followers",
                1 if amount == 0 or amount is None else (0 - amount)
            )

        return ToggleFollowUser(
            ok=ok,
            errors=errors,
        )


class ToggleFollowShop(ObjectMutation):
    ok = Boolean(required=True)
    errors = List(String, required=False)

    class Arguments:
        toShopId = ID(required=True)

    async def mutate(self, info, **kwargs):
        """
            get following relation ship(s) between this user and a shop
            if exists:
                delete it
            else:
                add one.
        """
        ok, errors = False, list()
        # check authentication:
        followingRelationShipToRemove = None
        user = info.context["request"].user
        toShopId = kwargs.get("toShopId", None)
        if user.is_authenticated:
            # get this user id:
            myUserId = getattr(user, "id", None)
            if myUserId is not None and myUserId != "":
                if toShopId is not None and toShopId != "":
                    try:
                        followingRelationShipGenerator = USER_FOLLOWING_RELATIONSHIP_COLLECTION.where(
                            u"from_user_id",
                            u"==",
                            u"{}".format(myUserId)
                        ).where(
                            u"to_shop_id",
                            u"==",
                            u"{}".format(toShopId)
                        ).stream()
                    except Exception as e:
                        logging.error(f"Error fetching following \
                            relation ships between user and shops: {e}")
                    else:
                        followingRelationShips = [
                            item for item in followingRelationShipGenerator
                        ]
                        if len(followingRelationShips):
                            # delete one by one
                            followingRelationShipToRemove = followingRelationShips
                            ok = True
                        else:
                            try:
                                USER_FOLLOWING_RELATIONSHIP_COLLECTION.add({
                                    u"from_user_id": myUserId,
                                    u"to_shop_id": toShopId,
                                })
                            except Exception as e:
                                logging.info(f"Error adding relation \
                                    ship: {e}, {ToggleFollowShop.__name__}")
                            else:
                                ok = True
                else:
                    errors.append("You need to provide an id.")
            else:
                logging.info(f"Error getting request \
                    user id: {ToggleFollowShop.__name__!r}")
        else:
            errors.append("You have to login to follow a shop.")

        if ok:
            background = info.context["background"]
            amount = len(followingRelationShipToRemove)
            if isinstance(followingRelationShipToRemove, list) and amount > 0:
                background.add_task(
                    remove_documents_from_a_collection,
                    followingRelationShipToRemove
                )
            # IMPORTANT: increase or decrease field "number_of_followers"
            background.add_task(
                increase_or_decrease_a_document_field,
                SHOP_COLLECTION,
                toShopId,
                u"number_of_followers",
                1 if amount == 0 or amount is None else (0-amount)
            )

        return ToggleFollowShop(
            ok=ok,
            errors=errors
        )


class Mutation(ObjectType):
    toggle_follow_user = ToggleFollowUser.Field()
    toggle_follow_shop = ToggleFollowShop.Field()
