from graphene import List, ObjectType, ID


class ProductImageType(ObjectType):
    id = ID(required=False)
