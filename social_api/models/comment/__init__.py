from social_api import firestoreDB


product_comment_name: str = "product_comment"
PRODUCT_COMMENT_COLLECTION = firestoreDB.collection(
    u"{}".format(product_comment_name)
)
