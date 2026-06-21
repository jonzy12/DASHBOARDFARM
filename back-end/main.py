from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import user_routes, fields_routes 


app = FastAPI(title="DASHFARMBOARD API")

origins = [
    "http://localhost:5173",  
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)


app.include_router(user_routes.router)
app.include_router(fields_routes.router)

@app.get("/")
async def root():
    return {"message": "running!"}
