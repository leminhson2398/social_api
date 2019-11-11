from social_api import firestoreDB

category_collection_name: str = "category"

CATEGORY_COLLECTION = firestoreDB.collection(
    u"{}".format(category_collection_name)
)

# fetch list of categories in every project restarting time
