from graphene import ObjectType, ID, String, Boolean, Int, List, Decimal


class ProductType(ObjectType):
    id          = ID(required=True)
    title       = String(required=True)
    shop_id     = ID(required=True)
    description = String(required=True)
    total_items = Int(required=True, default_value=0)
    views       = Int(required=True, default_value=0)
    categories  = List(ID, required=True)
    price       = Decimal(required=True, default_value=0)
    available   = Boolean(required=True, default_value=True)
