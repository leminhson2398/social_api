from graphene import Schema
from fastapi import FastAPI
from graphql.execution.executors.asyncio import AsyncioExecutor
from .models.schema import Query, Mutation
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from .middleware.auth import AuthBackend
from .models.file import routes, mutation
from .graphqlRunner import GraphQLApp


origins: list = [
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]


app = FastAPI()
# includes routes:
app.include_router(
    routes.router,
    prefix="/file"
)
# apply middlewares:
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())


app.add_route(
    "/",
    GraphQLApp(
        schema=Schema(query=Query, mutation=Mutation, types=[mutation.Upload]),
        executor_class=AsyncioExecutor
    ),
)
