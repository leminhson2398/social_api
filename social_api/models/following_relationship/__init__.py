from social_api import firestoreDB

# database collection name:
user_following_relationship = "user_following_relationship"

USER_FOLLOWING_RELATIONSHIP_COLLECTION = firestoreDB.collection(
    u"{0}".format(user_following_relationship)
)
