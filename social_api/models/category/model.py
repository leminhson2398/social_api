from graphene import ObjectType, String, ID


class CategoryType(ObjectType):
    id      = ID(required=True)
    name    = String(required=True)
    slug    = String(required=True)
