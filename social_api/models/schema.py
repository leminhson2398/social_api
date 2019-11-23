from .user.schema import UserMutation, UserQuery
from .following_relationship.schema import FollowingRelationshipQuery, FollowingRelationshipMutation
from .shop.schema import ShopQuery
from .product.schema import ProductQuery
from .category.schema import CategoryQuery
from .file.schema import FileMutation


class Mutation(
    UserMutation,
    FollowingRelationshipMutation,
    FileMutation
):
    """
        All the mutations of the app
    """
    pass


class Query(
    UserQuery,
    FollowingRelationshipQuery,
    ShopQuery,
    ProductQuery,
    CategoryQuery
):
    """
        All the queries of the app
    """
    pass
