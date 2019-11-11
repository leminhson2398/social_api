from graphene import ObjectType, Field, ID
from .model import CategoryType
from json import load
from os import path


class Query(ObjectType):
    category = Field(
        CategoryType,
        required=True,
        id=ID(required=True)
    )

    async def resolve_category(self, info, **kwargs):
        """
            category lookup based on json file
        """
        jsonDataFileName: str = "categories_data.json"
        id: str = kwargs.get("id", "")
        if id != "":
            curDir = path.dirname(__file__)
            filePath = path.altsep.join([curDir, jsonDataFileName])
            with open(filePath, "rb") as dataFile:
                categoryData = load(dataFile)
                print(categoryData)
        return {"a": True}
