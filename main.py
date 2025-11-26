from fastapi import FastAPI, Header,HTTPException,Depends,BackgroundTasks,Request
from pydantic import BaseModel
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
import time
import jwt
from fastapi.middleware.cors import CORSMiddleware
import dotenv
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
LOG_FILE=Path(__file__).resolve().parent/"app.log"

logging.basicConfig(level=logging.INFO,format="%(asctime)s -%(levelname)s -%(message)s",handlers=[logging.FileHandler(LOG_FILE,encoding="utf-8"),logging.StreamHandler()])
logger=logging.getLogger("zahra_api")

load_dotenv()

app=FastAPI()

security=HTTPBearer()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request:Request, call_next):
    method=request.method
    url=request.url.path
    start_time=time.time()
    client_ip=request.client.host if request.client else "unknown"
    idem=request.headers.get("Idempotency-Key","N/A")
    auth=request.headers.get("Authorization","N/A")
    user_sub="anonymous"
    try:
        if auth.startswith("Bearer "):
            token=auth.split(" ")[1]
            payload=jwt.decode(token,SECRECT_KEY,algorithms=[ALGORITHM])
            user_sub=payload.get("sub","anonymous")
    except Exception as e:
        logger.warning(f"Failed to decode token:{e}")
    response=await call_next(request)
    timeSpentForResponse=time.time()-start_time
    logger.info(f"{client_ip} - {method} {url}"
                f"status={response.status_code} - "
                f"Idempotency-Key= {idem}"
                f"Process time={timeSpentForResponse:.3f}s")
    return response
class RequestModel(BaseModel):
    prompt:str

_idempotency_store={}

SECRECT_KEY=os.getenv("JWT_SECRET")
ALGORITHM=os.getenv("ALGORITHM","HS256")
IDEM_K_EXPIRY=int(os.getenv("IDEMPOTENCY_KEY_EXPIRY","86400"))
TOKEN_EXPIRY=int(os.getenv("TOKEN_EXPIRY","3600"))

if SECRECT_KEY is None:
    raise RuntimeError("JWT_SECRET environment variable is not set")


def _clear_expired_idempotency_keys():
    expired_keys=[]
    current_time=time.time()
    for k,v in _idempotency_store.items():
        if current_time-v[0]> IDEM_K_EXPIRY:
            expired_keys.append(k)
    for k in expired_keys:
        _idempotency_store.pop(k,None)
    logger.info(f"Cleared {len(expired_keys)}Expired idempotency keys.")

def create_token():
    payload={"sub":"anonymous_user",
             "issueTime":time.time(),
             "exp":time.time() + int(TOKEN_EXPIRY)}
    token=jwt.encode(payload,SECRECT_KEY,algorithm=ALGORITHM)
    
    return token

@app.post("/give_token")
def give_token():
    token=create_token()
    logger.info("Token sent")
    return {"token":token}

async def get_current_user(cred:HTTPAuthorizationCredentials=Depends(security)):
    token=cred.credentials
    try:
        payload=jwt.decode(token,SECRECT_KEY,algorithms=[ALGORITHM])
        current_user=payload.get("sub")
        if current_user is None:
            raise HTTPException(status_code=401,detail="Invalid authentication credentials")
        return current_user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401,detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401,detail="Invalid authentication credetials")
    
@app.post("/process")
async def process(bgTasks: BackgroundTasks,req:RequestModel,
                  idempotency_key:str=Header(None,alias="Idempotency-Key"),
                  current_user:str=Depends(get_current_user),
                  ):
    logger.info(f"The process end point called by {current_user}"
                f"idem_key:{idempotency_key}")
    if not idempotency_key:
        raise HTTPException(status_code=400,detail="Idempotency-key header is required")
    if idempotency_key in _idempotency_store:
        ts,status,response=_idempotency_store[idempotency_key]
        logger.info(f"Idempotent reply to this idempotency_key:{idempotency_key}"
                    f"Original ts:{ts} , status:{status}")
        return response
    prompt=req.prompt
    if prompt=="Joke":
        response={"response":"why didi the chicken cross the road? to get to the other side!"}
    elif prompt=="Quote":
        response={"response":"The only limit to our realization of tomorrow is our doubts of today."}
    else:
        raise HTTPException(status_code=400,detail="Invalid prompt")
    _idempotency_store[idempotency_key]=(time.time(),200,response)
    bgTasks.add_task(_clear_expired_idempotency_keys)
    logger.info(f"The process completed for user:{current_user}"
                f"idempotency={idempotency_key}")
    return response
                  
        

