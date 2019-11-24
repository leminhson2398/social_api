from social_api import firestoreDB

order_collection_name: str = "order"

ORDER_COLLECTION = firestoreDB.collection(u"{}".format(order_collection_name))
