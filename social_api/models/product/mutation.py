from graphene import Mutation as ObjectMutation, ID, Boolean, List, String, ObjectType, Int, NonNull
from .import PRODUCT_LIKE_COLLECTION, PRODUCT_COLLECTION, PRODUCT_REPORT_COLLECTION, PRODUCT_BOOKMARK_COLLECTION
from ..utils.utils import increase_or_decrease_a_document_field, remove_documents_from_a_collection
import logging


class ToggleLikeProduct(ObjectMutation):
    ok = Boolean(required=True)
    errorList = List(
        String,
        required=False,
    )

    class Arguments:
        toProductId = ID(required=True)

    async def mutate(self, info, **kwargs):
        """
            add 1 like to product and remove if exist
        """
        ok: bool = False
        errorList: list = list()
        user = info.context["request"].user
        existingLikeRelationDocuments: list = list()

        # check authenticated or not:
        if user.is_authenticated:
            toProductId: str = kwargs.get("toProductId", "").strip()
            myUserId: str = getattr(user, "id", "")
            if toProductId != "":
                if myUserId != "":
                    # loooking for like relations ship between this user and this product:
                    try:
                        fetchResultGenerator = PRODUCT_LIKE_COLLECTION.where(
                            u"from_user_id",
                            u"==",
                            u"{}".format(myUserId)
                        ).where(
                            u"to_product_id",
                            u"==",
                            u"{}".format(toProductId)
                        ).stream()
                    except Exception as e:
                        logging.error(f"Error getting user-product like: {e}.")
                    else:
                        for like in fetchResultGenerator:
                            existingLikeRelationDocuments.append(like)
                        if len(existingLikeRelationDocuments):
                            ok = True
                        else:
                            try:
                                PRODUCT_LIKE_COLLECTION.add({
                                    u"from_user_id": myUserId,
                                    u"to_product_id": toProductId
                                })
                            except Exception as e:
                                logging.error(f"Error like product: {e}.")
                            else:
                                ok = True
                else:
                    logging.error("Couldn't get user id.")
            else:
                errorList.append("Product id is required.")
        else:
            errorList.append("You have to logged in to like this product.")

        if ok and not len(errorList):
            background = info.context["background"]
            amount = len(existingLikeRelationDocuments)
            if amount:
                background.add_task(
                    remove_documents_from_a_collection,
                    existingLikeRelationDocuments
                )
            # IMPORTANT: you have to increase || decrease "number_of_likes" from ".models.ProductLikeType"
            background.add_task(
                increase_or_decrease_a_document_field,
                PRODUCT_COLLECTION,
                toProductId,
                "number_of_likes",
                1 if amount == 0 else -amount
            )

        return ToggleLikeProduct(
            ok=ok,
            errorList=errorList
        )


class ReportProduct(ObjectMutation):
    ok = Boolean(required=True)
    errors = List(
        String,
        required=False
    )

    class Arguments:
        toProductId = ID(required=True)
        product_problems = List(Int, required=True)
        description = String(required=True)
        confirmation = Boolean(required=False)

    async def mutate(self, info, **kwargs):
        """
            send a report if this user has not done yet
            "product_problems" can contains at most 3 problems
        """
        from google.cloud.firestore_v1.document import DocumentSnapshot
        ok, errors = False, list()
        user = info.context["request"].user

        if user.is_authenticated:
            # get this user id, refer to "middleware.auth.py"
            myUserId = getattr(user, "id", "")
            toProductId, product_problems, description, confirmation = [
                kwargs.get(key, "") for key in ["toProductId", "product_problems", "description", "confirmation"]
            ]
            if (toProductId == "") and (product_problems == [] or product_problems == "") and (description == ""):
                # it doesn't matter if an user submitted 'confirmation' or not
                errors.append("Please provide your information.")
            elif toProductId != "":
                if (product_problems == [] or product_problems == "") and (description == ""):
                    errors.append("Please enter the problems of this product.")
                else:
                    # check report exist or not:
                    if myUserId != "":
                        try:
                            reportsGenerator = PRODUCT_REPORT_COLLECTION.where(
                                u"to_product_id",
                                u"==",
                                u"{}".format(toProductId)
                            ).where(
                                u"from_user_id",
                                u"==",
                                u"{}".format(myUserId)
                            ).stream()
                        except Exception as e:
                            logging.error(f"Error fetching reports: {e}.")
                        else:
                            reportsList = [
                                report for report in reportsGenerator
                            ]
                            if len(reportsList):
                                # the user already reported this product.
                                # up date this product based on the new values:
                                yourReport = reportsList[0]
                                if isinstance(yourReport, DocumentSnapshot):
                                    try:
                                        yourReport.reference.update({
                                            u"from_user_id": myUserId,
                                            u"to_product_id": toProductId,
                                            u"product_problems": product_problems,
                                            u"description": description,
                                            u"confirmation": False if not isinstance(confirmation, bool) else confirmation
                                        })
                                    except Exception as e:
                                        logging.error(
                                            f"Error updating report: {e}."
                                        )
                                    else:
                                        ok = True
                                else:
                                    pass
                            else:
                                # create new report.
                                try:
                                    PRODUCT_REPORT_COLLECTION.add({
                                        u"from_user_id": myUserId,
                                        u"to_product_id": toProductId,
                                        u"product_problems": product_problems,
                                        u"description": description,
                                        u"confirmation": False if not isinstance(confirmation, bool) else confirmation
                                    })
                                except Exception as e:
                                    logging.error(
                                        f"Error reporting this product: {e}."
                                    )
                                else:
                                    ok = True
                    else:
                        errors.append(
                            "Error reporting this product. Please try again."
                        )
        else:
            errors.append("You have to login to report this product.")

        return ReportProduct(
            ok=ok,
            errors=errors
        )


class ToggleBookmarkProduct(ObjectMutation):
    """
        if product is already bookmarked by this user, delete the bookmark relationship
        if not:
            add 1 bookmark
    """
    ok = Boolean(required=True)
    errors = List(
        String,
        required=False
    )

    class Arguments:
        toProductId = ID(required=True)

    async def mutate(self, info, **kwargs):
        ok, errors = False, list()
        bookmarkListToRemove: list = list()

        user = info.context["request"].user
        if user.is_authenticated:
            myUserId = getattr(user, "id", "")
            toProductId = kwargs.get("toProductId", "").strip()
            if toProductId != "":
                if myUserId != "":
                    # check bookmark or not:
                    try:
                        bookmarkRelationGenerator = PRODUCT_BOOKMARK_COLLECTION.where(
                            u"from_user_id",
                            u"==",
                            u"{}".format(myUserId)
                        ).where(
                            u"to_product_id",
                            u"==",
                            u"{}".format(toProductId)
                        ).stream()
                    except Exception as e:
                        logging.error(f"Error fetching product bookmark: {e}.")
                    else:
                        for bookmark in bookmarkRelationGenerator:
                            bookmarkListToRemove.append(bookmark)
                        if len(bookmarkListToRemove):
                            ok = True
                        else:
                            # add bookmark:
                            try:
                                PRODUCT_BOOKMARK_COLLECTION.add({
                                    u"from_user_id": myUserId,
                                    u"to_product_id": toProductId
                                })
                            except Exception as e:
                                errors.append(
                                    "Error bookmarking this product.")
                                logging.error(f"Error adding bookmark: {e}.")
                            else:
                                ok = True
                else:
                    logging.error(
                        f"Error getting current user id: <{ToggleBookmarkProduct.__name__}>."
                    )
            else:
                errors.append("Error identifying product. Plese try again.")
        else:
            errors.append("You have to login to bookmark this product.")

        if ok and len(errors) == 0:
            background = info.context["background"]
            # delete existing bookmarks
            if len(bookmarkListToRemove):
                background.add_task(
                    remove_documents_from_a_collection,
                    bookmarkListToRemove,
                )

        return ToggleBookmarkProduct(
            ok=ok,
            errors=errors,
        )


class Mutation(ObjectType):
    toggle_like_product = ToggleLikeProduct.Field()
    report_a_product = ReportProduct.Field()
    toggle_bookmark_product = ToggleBookmarkProduct.Field()
