from graphene import ObjectType, Field, ID, NonNull, List
from .model import ShopType
from .import SHOP_COLLECTION
import logging
from ..import NUMBER_OF_RESULTS_A_TIME
# from google.cloud.firestore_v1 import DocumentSnapshot


class Query(ObjectType):
    shop = Field(
        ShopType,
        shipId=ID(required=True),
    )
    shops = NonNull(
        List(ShopType, required=False),
        nextShopId=ID(required=False)
    )

    async def resolve_shop(self, info, **kwargs):
        shop = None
        shopId = kwargs.get("shopId", None)
        if shopId and shopId != "":
            fetchResult = SHOP_COLLECTION.document(u"{}".format(shopId)).get()
            if fetchResult.exists:
                shop = fetchResult.to_dict()
                shop["id"] = shopId
        return shop

    async def resolve_shops(self, info, **kwargs):
        """
        get and paginate a list of shops from database
        param "nextShopId" is not required, pass in to determine the end cursor 
        for fetching other Documents that come after this
        """
        shops, shopSnapShot, fetchResult = list(), None, None
        nextShopId = kwargs.get("nextShopId", None)

        if nextShopId and nextShopId != "":
            # get the shop
            shopSnapShot = SHOP_COLLECTION.document(
                u"{}".format(nextShopId)
            ).get()
        # check "shopSnapShot" is "DocumentSnapShot" ot not:
        # then fetch database using "start_after" method
        if not shopSnapShot is None and shopSnapShot.exists:
            try:
                fetchResult = SHOP_COLLECTION.start_after(
                    shopSnapShot
                ).limit(NUMBER_OF_RESULTS_A_TIME).stream()
            except Exception as e:
                logging.info(f"Error fetching shops {e}")
        else:
            try:
                fetchResult = SHOP_COLLECTION.limit(
                    NUMBER_OF_RESULTS_A_TIME
                ).stream()
            except Exception as e:
                logging.info(f"Error fetching shops {e}")
        # parse data:
        for shop in fetchResult:
            shopData = shop.to_dict()
            shopData["id"] = shop.id
            shops.append(shopData)

        return shops
