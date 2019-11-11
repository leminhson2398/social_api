from social_api import firestoreDB

# the string "shop" get from firestore database
shop_collection: str = "shop"

SHOP_COLLECTION = firestoreDB.collection(u"{0}".format(shop_collection))
