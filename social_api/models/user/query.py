from graphene import ObjectType, ID, List, NonNull, Field
from .model import UserType
from .import USER_COLLECTION
import logging
from ..import NUMBER_OF_RESULTS_A_TIME


class Query(ObjectType):
    user = Field(
        UserType, required=False, id=ID(required=True)
    )
    users = NonNull(
        List(UserType, required=False),
        afterId=ID(required=False)
    )

    async def resolve_user(self, info, **kwargs):
        # print(info.context["request"].user.is_authenticated)
        user = None
        id = kwargs.get("id", "").strip()
        if id != "":
            try:
                userSnapshot = USER_COLLECTION.document(
                    u"{}".format(id)
                ).get()
                # check document existence
                if userSnapshot.exists:
                    # print(f"{userSnapshot.create_time!r}")
                    user = userSnapshot.to_dict()
                    # add id field to document
                    user["id"] = id
            except Exception as e:
                logging.error(f"error getting user by id: {e}")
        return user

    async def resolve_users(self, info, **kwargs):
        afterId = kwargs.get("afterId", "").strip()
        users = []
        userReferenceGenerator = None

        if afterId != "":
            try:
                userSnapshot = USER_COLLECTION.document(
                    u"{}".format(afterId)
                ).get()
            except Exception as e:
                logging.error(f"Error fetching user: {e}.")
            else:
                if userSnapshot.exists:
                    userReferenceGenerator = USER_COLLECTION.start_after(
                        userSnapshot
                    ).limit(NUMBER_OF_RESULTS_A_TIME).stream()
        else:
            userReferenceGenerator = USER_COLLECTION.limit(
                NUMBER_OF_RESULTS_A_TIME
            ).stream()
        for user in userReferenceGenerator:
            userDate = user.to_dict()
            userDate["id"] = user.id
            users.append(userDate)
        return users
