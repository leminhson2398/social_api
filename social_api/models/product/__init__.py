from social_api import firestoreDB

product_collection_name: str = "products"
product_bookmark_collection_name: str = "product_bookmark"
product_like_collection_name: str = "product_like"
product_report_collection_name: str = "product_report"

PRODUCT_COLLECTION = firestoreDB.collection(
    u"{}".format(product_collection_name))
PRODUCT_BOOKMARK_COLLECTION = firestoreDB.collection(
    u"{}".format(product_bookmark_collection_name))
PRODUCT_LIKE_COLLECTION = firestoreDB.collection(
    u"{}".format(product_like_collection_name))
PRODUCT_REPORT_COLLECTION = firestoreDB.collection(
    u"{}".format(product_report_collection_name))
