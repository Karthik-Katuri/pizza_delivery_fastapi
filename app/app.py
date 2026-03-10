from fastapi import FastAPI
from app.auth_routes import auth_router
from app.order_routes import order_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(order_router)




@app.get("/hello")
async def hello_world(name: str):
    return {"message": f"hello {name}"}
