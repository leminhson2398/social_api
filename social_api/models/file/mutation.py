from graphene import ObjectType, Mutation as ObjectMutation, Boolean, List, String, NonNull
from graphene.types import Scalar


class Upload(Scalar):
    """Create scalar that ignores normal serialization/deserialization, since
    that will be handled by the multipart request spec"""

    @staticmethod
    def serialize(value):
        return value

    @staticmethod
    def parse_literal(node):
        return node

    @staticmethod
    def parse_value(value):
        return value


class FileUpload(ObjectMutation):
    class Input:
        files = NonNull(
            List(Upload, required=True)
        )
        text = String(required=False)

    ok = Boolean(required=True)
    errors = List(String, required=False)

    async def mutate(self, info, **kwargs):
        print(kwargs)

        return FileUpload(
            ok=True,
            errors=None
        )


class Mutation(ObjectType):
    upload_file = FileUpload.Field()
