from graphene import ObjectType, ID, String


class ProductCommentType(ObjectType):
    id = ID(required=True)
    text = String(required=True)
