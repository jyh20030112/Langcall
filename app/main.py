from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.mail import router as mail_router
from app.api.routes.reports import router as reports_router
from app.api.routes.webhooks import router as webhook_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="LangCall minimal FastAPI app with LangGraph-backed call processing.",
)

app.include_router(health_router)
app.include_router(mail_router)
app.include_router(reports_router)
app.include_router(webhook_router)


def main() -> None:
    print(f"{settings.app_name} is ready.")
    print("Run `uvicorn app.main:app --reload` to start the FastAPI server.")
    print("Run `python scripts/run_demo.py` to execute the script-based demo.")


if __name__ == "__main__":
    main()
