from social_api import firestoreDB
from os import path
import logging
import json
# import typing


category_collection_name: str = "category"

CATEGORY_COLLECTION = firestoreDB.collection(
    u"{}".format(category_collection_name)
)

# fetch list of categories in every project restarting time
# rawDataFileName: str = "raw_data.json"
productionFileName: str = "production_data.json"

curDir: str = path.dirname(path.abspath(__file__))
# rawDataPath: str = path.join(curDir, rawDataFileName)
productionPath: str = path.join(curDir, productionFileName)

with open(productionPath, "w") as productionFile:
    # fetch all categories:
    categoryList: list = list()
    try:
        fetchResult = CATEGORY_COLLECTION.stream()
    except Exception as e:
        logging.error(f"Error fetching categories from database: {e}.")
    else:
        for category in fetchResult:
            categoryData = category.to_dict()
            categoryData["id"] = category.id
            categoryList.append(categoryData)

    if len(categoryList) > 0:
        json.dump(categoryList, productionFile)


# if path.exists(rawDataPath) and path.exists(productionPath):
#     # compare data in two files,
#     rawData = None
#     productionData = None
#     with open(rawDataPath, "r") as rawFile:
#         try:
#             rawData = json.load(rawFile)
#         except Exception as e:
#             logging.error(f"Error loading raw json file: {e}.")
#     with open(productionPath, "r") as productionFile:
#         try:
#             productionData = json.load(productionFile)
#         except Exception as e:
#             logging.error(f"Error loading production json file: {e}.")

#     if (not rawData is None and isinstance(rawData, list)) and \
#             (not productionData is None and isinstance(productionData, list)):
#         # declare function checking existance of items inside two data list:
#         def checkExist(item: typing.Any) -> bool:
#             for itm in productionData:
#                 name = itm.get("name", None)
#                 if not name is None:
#                     if name == item["name"]:
#                         return True
#             return False
#         for data in rawData:
#             name: str = data.get("name", None)


# if path.exists(rawDataPath) and path.isfile(rawDataPath):
#     # batch write:
#     batch = firestoreDB.batch()
#     try:
#         with open(rawDataPath, "r") as jsonFile:
#             rawCategories: typing.Any = json.load(jsonFile)
#             if isinstance(rawCategories, list) and len(rawCategories) > 0:
#                 for category in rawCategories:
#                     name: str = category.get("name", None)
#                     docRef: typing.Any = CATEGORY_COLLECTION.document()
#                     # set data for each
#                     batch.set(docRef, {u"name": u"{}".format(name)})
#                 # commit batch
#                 batch.commit()
#     except Exception as e:
#         logging.error(f"Error opening raw category file: {e}.")
