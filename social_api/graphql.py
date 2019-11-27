import json
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.requests import Request
from starlette.background import BackgroundTasks
from starlette import status
from starlette.graphql import GraphQLApp


try:
    from graphql.error import format_error as format_graphql_error
except ImportError:  # pragma: nocover
    format_graphql_error = None  # type: ignore


class CustomGraphqlApp(GraphQLApp):

    async def handle_graphql(self, request: Request) -> Response:
        if request.method in ("GET", "HEAD"):
            if "text/html" in request.headers.get("Accept", ""):
                if not self.graphiql:
                    return PlainTextResponse(
                        "Not Found", status_code=status.HTTP_404_NOT_FOUND
                    )
                return await self.handle_graphiql(request)

            # type: typing.Mapping[str, typing.Any]
            data = request.query_params

        elif request.method == "POST":
            content_type = request.headers.get("Content-Type", "")

            if "application/json" in content_type:
                data = await request.json()
                # data gonna look like this:
                """
					{
					'operationName': 'Signin', 
					'variables': {'email': 'leminhson2398@gmail.com.uk', 'password': 'Anhyeuem98@'}, 
					'query': 'mutation Signin($email: String!, $password: String!) {\n  signin(email: $email, password: $password) {\n    ok\n    errorList\n    token\n   __typename\n  }\n}\n'
					}
					"""
            elif "application/graphql" in content_type:
                body = await request.body()
                text = body.decode()
                data = {"query": text}
            elif "query" in request.query_params:
                data = request.query_params
            elif "multipart/form-data" in content_type:
                form = await request.form()
                form: dict = dict(form)
                data: dict = json.loads(form.pop('operations', None))
                map_: dict = json.loads(form.pop('map', None))
                variables: dict = data.get('variables', None)
                if variables is not None:
                    for key in variables.keys():
                        # check if field is None or list of Nones
                        if not bool(variables[key]) or not all(variables[key]):
                            varValue: list = [
                                form.get(k, None) for k in map_.keys()
                            ]
                            variables.update({
                                key: varValue
                            })
                            data.update({
                                'variables': variables
                            })
                # form gonna looks like this:
                """
					{
						'operations': '{
							"operationName":"UploadFile",
							"variables":{"file":null},
							"query":"mutation UploadFile($file: Upload!) {\\n  uploadFile(file: $file) {\\n    ok\\n   errors\\n    __typename\\n  }\\n}\\n"
						}',
						'map': '{"1":["variables.file"]}',
						'1': <starlette.datastructures.UploadFile object at 0x0000025395E7C1C8>,
						...
					}
					"""
            else:
                return PlainTextResponse(
                    "Unsupported Media Type",
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                )

        else:
            return PlainTextResponse(
                "Method Not Allowed", status_code=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        try:
            query = data["query"]
            variables = data.get("variables")
            operation_name = data.get("operationName")
        except KeyError:
            return PlainTextResponse(
                "No GraphQL query found in the request",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        background = BackgroundTasks()
        context = {"request": request, "background": background}

        result = await self.execute(
            query, variables=variables, context=context, operation_name=operation_name
        )
        error_data = (
            [format_graphql_error(err) for err in result.errors]
            if result.errors
            else None
        )
        response_data = {"data": result.data, "errors": error_data}
        status_code = (
            status.HTTP_400_BAD_REQUEST if result.errors else status.HTTP_200_OK
        )

        return JSONResponse(
            response_data, status_code=status_code, background=background
        )
