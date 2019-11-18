from graphene import ObjectType, Field, ID, NonNull, List
from .model import CategoryType
import typing
import logging
from ..utils.utils import slugify


def jsonFetcher() -> typing.Any:
    import json
    import os

    categoryDataFileName: str = "production_data.json"
    categoryFilePath: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        categoryDataFileName
    )
    if os.path.exists(categoryFilePath) and os.path.isfile(categoryFilePath):
        try:
            with open(categoryFilePath, "r", encoding="utf-8") as categoryFile:
                try:
                    categories: typing.Any = json.load(categoryFile)
                except Exception as e:
                    logging.error(f"Error loading data json: {e}.")
        except Exception as e:
            logging.error(f"Error opening category file: {e}.")

    async def getData(categoryIds) -> typing.Any:
        if len(categoryIds) == 1:
            for category in categories:
                if category["id"] == categoryIds[0].strip():
                    return category
            # if couldn't find any item satisfies:
            return None
        else:
            # the categoryIds has more than 1:
            return filter(lambda item: any([item["id"] == id for id in categoryIds]), categories)

    return getData


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
