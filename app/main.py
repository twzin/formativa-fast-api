from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import json
from datetime import datetime
import time

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

usuario_teste = {"username": "admin", "password": "1234"}

metrics = {
    "total_requests": 0,
    "total_errors": 0,
    "failed_logins": 0
}

# LOG

logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()

def format_log(level, message, request: Request = None, response_time=None):
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "endpoint": request.url.path if request else "N/A",
        "ip": request.client.host if request else "N/A",
        "message": message
    }

    if response_time is not None:
        log["response_time_ms"] = round(response_time * 1000, 2)

    return json.dumps(log)

handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(handler)

file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(file_handler)

# Middleware

@app.middleware("http")
async def before(request: Request, call_next):
    start_time = time.time()

    metrics["total_requests"] += 1
    logger.info(format_log("INFO", "Acesso ao endpoint", request))

    try:
        response = await call_next(request)

        response_time = time.time() - start_time

        if response.status_code >= 400:
            metrics["total_errors"] += 1

        logger.info(format_log("INFO", "Resposta enviada", request, response_time))

        return response

    except Exception as e:
        metrics["total_errors"] += 1
        logger.error(format_log("ERROR", str(e), request))
        return JSONResponse(status_code=500, content={"message": "Erro interno"})

# Endpoints

@app.get("/health")
async def health(request: Request):
    logger.info(format_log("INFO", "Healthcheck executado", request))
    return {"status": "OK"}

@app.get("/metrics")
async def get_metrics(request: Request):
    logger.info(format_log("INFO", "Consulta de métricas", request))
    return metrics

@app.post("/login")
async def login(data: LoginRequest, request: Request):
    try:
        if data.username == usuario_teste["username"] and data.password == usuario_teste["password"]:
            logger.info(format_log("INFO", f"Login bem-sucedido para {usuario_teste['username']}", request))
            return {"message": "Login OK"}

        else:
            metrics["failed_logins"] += 1
            logger.warning(format_log("WARNING", "Login falhou", request))
            return JSONResponse(status_code=401, content={"message": "Credenciais inválidas"})

    except Exception as e:
        metrics["total_errors"] += 1
        logger.error(format_log("ERROR", str(e), request))
        return JSONResponse(status_code=500, content={"message": "Erro interno"})
    