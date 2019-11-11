from graphene import Boolean, ObjectType, Mutation as ObjectMutation
from graphene_file_upload.scalars import Upload
from starlette.requests import Request


# class UploadFile(ClientIDMutation):
#     class Input:
#         pass

#     ok = Boolean(required=True)

#     @classmethod
#     async def mutate_and_get_payload(cls, root, info, **kwargs):
#         form = await info.context["request"].form()
#         print(form)

#         return UploadFile(
#             ok=True,
#         )

class UploadFile(ObjectMutation):
    ok = Boolean(required=True)

    class Arguments:
        file = Upload(required=True)

    async def mutate(self, info, file):
        # print(dir(info.context["request"]))
        print(file)
        form = await info.context["request"].form()
        print(form)

        return UploadFile(
            ok=True
        )


class Mutation(ObjectType):
    upload_file = UploadFile.Field()
