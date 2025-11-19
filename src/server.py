# load env from the top
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from starlette_graphene3 import GraphQLApp, make_playground_handler
from src.graphQL.schema import schema
from lib.ap_scheduler import background_tasks
from src.auth.routes import auth_routes

app = FastAPI()

# invoke the background tasks during app startup
background_tasks()

# include the auth router in the app
app.include_router(prefix="/api/v1", router=auth_routes)


@app.get("/api/v1")
def read_root():
    return {"Hello": "World"}


app.mount("/api/v1/graphql", GraphQLApp(schema, on_get=make_playground_handler()))
