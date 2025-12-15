from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import task, generate, history, auth
from app.routers import admin, plan, quota

app = FastAPI(title="AI Web Platform Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task.router)
app.include_router(generate.router)
app.include_router(history.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(plan.router)
app.include_router(quota.router)

@app.get("/")
def root():
    return {"msg": "Backend is running"}
