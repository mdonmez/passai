import logging
import os
import base64
from pathlib import Path
from functools import lru_cache
from time import perf_counter
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import instructor
from litellm import completion
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

from pass_generator import PassGenerator
from data.models import PassParams

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

if not STATIC_DIR.exists():
    raise RuntimeError(f"Static directory not found: {STATIC_DIR}")
if not TEMPLATES_DIR.exists():
    raise RuntimeError(f"Templates directory not found: {TEMPLATES_DIR}")


@lru_cache(maxsize=1)
def get_llm_instruction() -> str:
    try:
        return LLM_INSTRUCTION_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.error(f"LLM instruction file not found: {LLM_INSTRUCTION_PATH}")
        raise


client = instructor.from_litellm(completion, mode=instructor.Mode.JSON)
pass_generator = PassGenerator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting passai application...")
    _ = pass_generator.word_list
    logger.info("Word list preloaded successfully")
    yield
    logger.info("Shutting down passai application...")


app = FastAPI(
    title="passai",
    description="AI-powered password generator",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{perf_counter() - start_time:.4f}"
    return response


templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    logger.error("API_KEY environment variable is required")
    raise ValueError("API_KEY environment variable must be set")

LLM_MODEL = os.getenv("LLM_MODEL", "gemini/gemini-2.0-flash-exp")
LLM_INSTRUCTION_PATH = Path("data/llm_instruction.md")


class GenerateRequest(BaseModel):
    input: str = Field(..., min_length=1, description="User's password requirements")
    publicKey: str = Field(..., description="Client's public key for encryption")


class GenerateResponse(BaseModel):
    encryptedPass: str = Field(..., description="Encrypted password")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")


def encrypt_password(password: str, public_key_pem: str) -> str:
    try:
        public_key_bytes = base64.b64decode(public_key_pem)
        public_key = serialization.load_pem_public_key(public_key_bytes)
        encrypted = public_key.encrypt(  # type: ignore[union-attr]
            password.encode("utf-8"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return base64.b64encode(encrypted).decode("utf-8")
    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        raise ValueError("Failed to encrypt password")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post(
    "/generate",
    response_model=GenerateResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def generate_pass(request: GenerateRequest):
    try:
        user_input = request.input.strip()
        public_key = request.publicKey

        if not user_input:
            raise HTTPException(
                status_code=400, detail="Please enter a description for your pass"
            )

        if not public_key:
            raise HTTPException(
                status_code=400, detail="Public key required for secure transmission"
            )

        logger.info(f"Processing request: {user_input[:50]}...")

        pass_config = client.chat.completions.create(
            model=LLM_MODEL,
            api_key=API_KEY,
            messages=[
                {"role": "system", "content": get_llm_instruction()},
                {"role": "user", "content": user_input},
            ],
            response_model=PassParams,
            max_retries=2,
        )

        if pass_config.type == "password" and pass_config.password:
            result = pass_generator.generate_password(
                **pass_config.password.model_dump()
            )
        elif pass_config.type == "passphrase" and pass_config.passphrase:
            result = pass_generator.generate_passphrase(
                **pass_config.passphrase.model_dump()
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid pass configuration")

        encrypted_pass = encrypt_password(result, public_key)

        logger.info("Successfully generated and encrypted pass")
        return GenerateResponse(encryptedPass=encrypted_pass)

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating pass: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to generate pass. Please try again."
        )


if __name__ == "__main__":
    import uvicorn

    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))

    logger.info(
        f"Starting application in {'debug' if debug_mode else 'production'} mode"
    )
    uvicorn.run("app:app", host=host, port=port, reload=debug_mode, log_level="info")
