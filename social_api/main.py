from graphene import Schema
from fastapi import FastAPI
from starlette.graphql import GraphQLApp
from graphql.execution.executors.asyncio import AsyncioExecutor
from .models.schema import Query, Mutation
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from .middleware.auth import AuthBackend


origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:3000"
    "http://localhost:3000",
]


app = FastAPI()
# apply middlewares:
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())


@app.post("/upload")
async def upload(request):
    form = await request.form()
    print(form)


app.add_route(
    "/",
    GraphQLApp(
        schema=Schema(query=Query, mutation=Mutation), executor_class=AsyncioExecutor
    ),
)
