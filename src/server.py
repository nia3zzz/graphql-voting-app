from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from starlette_graphene3 import GraphQLApp, make_playground_handler
from graphQL.schema import schema

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.mount("/", GraphQLApp(schema, on_get=make_playground_handler()))
