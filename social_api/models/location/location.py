from graphene import Float, ObjectType, Mutation as ObjectMutation, Boolean


class LocationType(ObjectType):
    latitude = Float(required=False)
    longitude = Float(required=False)

