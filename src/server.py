# load env from the top
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from starlette_graphene3 import GraphQLApp, make_playground_handler
from src.graphQL.schema import schema
from lib.ap_scheduler import background_tasks

app = FastAPI()

# invoke the background tasks during app startup
background_tasks()


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.mount("/", GraphQLApp(schema, on_get=make_playground_handler()))
