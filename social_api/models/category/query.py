from graphene import ObjectType, Field, ID, NonNull, List
from .model import CategoryType
import logging
from ..utils.utils import slugify
from .import jsonFetcher


categoryData = jsonFetcher()


class Query(ObjectType):
    category = Field(
        CategoryType,
        id=ID(required=True)
    )

    categories = NonNull(
        List(CategoryType),
        ids=List(ID, required=True)
    )

    async def resolve_category(self, info, **kwargs):
        """
            category lookup based on json file
        """
        id: str = kwargs.get("id", "").strip()
        data = None
        if id != "":
            data = await categoryData(id)
            if not data is None:
                data["slug"] = slugify(data["name"])

        else:
            logging.error(f"Error fetching category item in file: {__file__}.")

        return data

    async def resolve_categories(self, info, **kwargs):
        """
            finding all categories that have ids exist in "ids" argument:
        """
        ids: list = kwargs.get("ids", [])
        result: list = list()
        if len(ids) > 0:
            for data in await categoryData(ids):
                data["slug"] = slugify(data["name"])
                result.append(data)

        return result
