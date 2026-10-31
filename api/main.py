from fastapi import FastAPI

from api.routes.learners import router as learners_router
from api.routes.tutor import router as tutor_router

app = FastAPI(
    title="Educentriks Cognify API",
    description="Adaptive AI certification learning coach by Educentriks",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Educentriks Cognify",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "educentriks-api",
    }


app.include_router(learners_router)
app.include_router(tutor_router)
