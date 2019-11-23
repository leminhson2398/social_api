from graphene import ObjectType, Mutation as ObjectMutation, Boolean, List, String, types, Scalar


class Upload(Scalar):
    def serialize(self):
        pass


class FileUpload(ObjectMutation):
    class Input:
        file = Upload()
        # id = String(required=True)

    ok = Boolean(required=True)
    errors = List(String, required=False)

    @staticmethod
    async def mutate(root, args, context, info):
        # client_signature = files['variables.signature']
        print(root)
        print(args)
        print(context)
        print(info)

        return FileUpload(
            ok=True,
            errors=None
        )


class Mutation(ObjectType):
    upload_file = FileUpload.Field()
