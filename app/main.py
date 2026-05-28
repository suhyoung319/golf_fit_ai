from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.routers import recommend

app = FastAPI(
    title="Golf Fit AI",
    description="골프 실력 기반 클럽 추천 시스템",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(recommend.router, prefix="/api", tags=["추천"])


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """메인 추천 페이지."""
    return templates.TemplateResponse("index.html", {"request": request})
