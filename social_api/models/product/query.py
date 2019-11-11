from graphene import ObjectType, ID, String, NonNull, List
from .model import ProductType
from .import PRODUCT_COLLECTION
import logging
from ..import NUMBER_OF_RESULTS_A_TIME


class Query(ObjectType):
    products_by_category_id = NonNull(
        List(ProductType, required=False),
        categoryId=ID(required=True),
        afterId=ID(required=False),
    )

    products_by_shop_id = NonNull(
        List(ProductType, required=False),
        shopId=ID(required=True),
        afterId=ID(required=False),
    )

    async def resolve_products_by_category_id(self, info, **kwargs):
        """
        fetch all products that have the same category id in their categories field
        """
        products, cursorProductSnapShot, fetchGenerator = list(), None, None

        categoryId, afterId = [
            kwargs.get(key, None) for key in ["categoryId", "afterId"]
        ]
        if afterId and afterId != "":
            # fetch cursor first:
            try:
                cursorProductSnapShot = PRODUCT_COLLECTION.document(
                    u"{}".format(afterId)
                ).get()
            except Exception as e:
                logging.info(f"Error fetching product cursor: {e}.")
                pass

        if not cursorProductSnapShot is None and cursorProductSnapShot.exists:
            # fetch results come after this cursor:
            try:
                fetchGenerator = PRODUCT_COLLECTION.where(
                    u"categories",
                    u"array_contains",
                    u"{}".format(categoryId)
                ).start_after(
                    cursorProductSnapShot
                ).limit(NUMBER_OF_RESULTS_A_TIME).stream()
            except Exception as e:
                logging.info("Error fetching products list: {e}.")
                pass
        else:
            try:
                fetchGenerator = PRODUCT_COLLECTION.where(
                    u"categories",
                    u"array_contains",
                    u"{}".format(categoryId)
                ).limit(NUMBER_OF_RESULTS_A_TIME).stream()
            except Exception as e:
                logging.info(f"Error fetching products list: {e}.")

        for product in fetchGenerator:
            productData = product.to_dict()
            productData["id"] = product.id
            products.append(productData)

        return products

    async def resolve_products_by_shop_id(self, info, **kwargs):
        """
            fetch all products of a shop (10 at a time)
            "afterId" is for pagination.
        """
        shopId, afterId = [
            kwargs.get(key, None) for key in ["shopId", "afterId"]
        ]
        products, cursorProductSnapshot, fetchResultGenerator = list(), None, None
        if not shopId is None and shopId != "":
            # if pagination is needed:
            if not afterId is None and afterId != "":
                try:
                    cursorProductSnapshot = PRODUCT_COLLECTION.document(
                        u"{}".format(afterId)
                    ).get()
                except Exception as e:
                    logging.info(f"Error fetching snapshot <{e}>.")
                    pass

            if not cursorProductSnapshot is None and cursorProductSnapshot.exists:
                try:
                    fetchResultGenerator = PRODUCT_COLLECTION.where(
                        u"shop_id",
                        u"==",
                        u"{}".format(shopId)
                    ).start_after(
                        cursorProductSnapshot
                    ).limit(NUMBER_OF_RESULTS_A_TIME).stream()
                except Exception as e:
                    logging.info(f"Error fetching products: <{e}>.")
                    pass
            else:
                try:
                    fetchResultGenerator = PRODUCT_COLLECTION.where(
                        u"shop_id",
                        u"==",
                        u"{}".format(shopId)
                    ).limit(NUMBER_OF_RESULTS_A_TIME).stream()
                except Exception as e:
                    logging.info(f"Error fetching products: <{e}>.")
                    pass

            # check "fetchResultGenerator" value:
            if not fetchResultGenerator is None:
                for product in fetchResultGenerator:
                    productData = product.to_dict()
                    productData["id"] = product.id
                    products.append(productData)
        else:
            logging.info(f"Must provide a shop id.")

        return products
