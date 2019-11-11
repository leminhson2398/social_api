from social_api import firestoreDB

product_collection: str = "products"

PRODUCT_COLLECTION = firestoreDB.collection(u"{}".format(product_collection))
