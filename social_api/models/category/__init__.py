from social_api import firestoreDB
import logging
import typing


category_collection_name: str = "category"

CATEGORY_COLLECTION = firestoreDB.collection(
    u"{}".format(category_collection_name)
)


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
