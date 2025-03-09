import json
import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel

# --- VERSION ---
BUILD = 4
VERSION = "1.1"


# Environment
load_dotenv()
API_TOKEN = os.getenv("TALLYBOX_API_TOKEN", default=None) # def for tokens below if they not present
API_GET_TOTAL_TOKEN = os.getenv("TALLYBOX_API_GET_TOTAL_TOKEN", default=API_TOKEN) # for /total
API_GET_HISTORY_TOKEN = os.getenv("TALLYBOX_API_GET_HISTORY_TOKEN", default=API_TOKEN) # for /history
API_SET_TOKEN = os.getenv("TALLYBOX_API_SET_TOKEN", default=API_TOKEN) # token for /change and /data
DATA_DIR_PATH = os.getenv("TALLYBOX_DATA_DIR_PATH") # required, data dir

missing_vars = []
if DATA_DIR_PATH is None:
    missing_vars.append("[TALLYBOX_DATA_DIR_PATH]")
if API_GET_TOTAL_TOKEN is None:
    missing_vars.append("[TALLYBOX_API_GET_TOTAL_TOKEN or TALLYBOX_API_TOKEN]")
if API_GET_HISTORY_TOKEN is None:
    missing_vars.append("[TALLYBOX_API_GET_HISTORY_TOKEN or TALLYBOX_API_TOKEN]")
if API_SET_TOKEN is None:
    missing_vars.append("[TALLYBOX_API_SET_TOKEN or TALLYBOX_API_TOKEN]")

if missing_vars:
    raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

DATA_TOTAL_FILE = f"{DATA_DIR_PATH}/total.txt"
DATA_HISTORY_FILE = f"{DATA_DIR_PATH}/history.json"
DATA_VERSION_FILE = f"{DATA_DIR_PATH}/version.txt"

# set version.txt file for feature...
def set_ver():
    with open(DATA_VERSION_FILE, 'w') as f:
        f.write(f"tallybox:{BUILD}")

set_ver()

# Data handler for 'data' variable
class TallyBoxData:
    def __init__(self, total, history):
        self.total = total
        self.history = history

    def save(self):
        """Save object to DATA_DIR_PATH"""
        with open(DATA_TOTAL_FILE, 'w') as f:
            f.write(str(self.total))

        with open(DATA_HISTORY_FILE, 'w') as f:
            f.write(json.dumps(self.history))

def load() -> TallyBoxData:
    """Load a TallyBoxData object from DATA_DIR_PATH (if exists, otherwise create default)"""
    _total = 0
    _history = []
    c = 2
    if os.path.exists(DATA_TOTAL_FILE):
        with open(DATA_TOTAL_FILE, 'r') as f:
            _total = int(str(f.read()))
        c -= 1

    if os.path.exists(DATA_HISTORY_FILE):
        with open(DATA_HISTORY_FILE, 'r') as f:
            _history = json.loads(str(f.read()))
        c -= 1

    obj = TallyBoxData(_total, _history)
    if c > 0:
        obj.save()
    return obj


### Application
app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
security = HTTPBearer()
data = load() # Restore a TallyBoxData from files

def verify_token(token: str, expected_token: str) -> bool:
    return token == expected_token

def throw_if_token_bad(token, expected):
    if not verify_token(token.credentials, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")

# Endpoints
@app.get("/total")
async def get_total(token = Depends(security)):
    throw_if_token_bad(token, API_GET_TOTAL_TOKEN)
    return {"total": data.total}

@app.get("/history")
async def get_history(token = Depends(security)):
    throw_if_token_bad(token, API_GET_HISTORY_TOKEN)
    return {"history": data.history}

@app.get("/data")
async def get_data(token = Depends(security)):
    throw_if_token_bad(token, API_SET_TOKEN)
    return {"history": data.history, "total": data.total}

class ChangeRequest(BaseModel):
    amount: float
    comment: str

@app.post("/change")
async def post_change(request: ChangeRequest, token = Depends(security)):
    throw_if_token_bad(token, API_SET_TOKEN)
    if request.comment is None:
        raise HTTPException(status_code=500, detail="Comment is required")

    if len(request.comment) > 1024*8:
        raise HTTPException(status_code=500, detail="Comment too big")

    data.total = data.total + int(request.amount)
    history_record = {
        "comment": request.comment.strip(),
        "amount": round(request.amount),
        "timestamp": round(time.time()),
    }
    data.history.append(history_record)
    data.save()

    return {"success": True, "total": data.total, "history_record": history_record}

if __name__ == "__main__":
    import uvicorn
    print(f"Starting TallyBox v{VERSION} ({BUILD})")
    uvicorn.run(app, host="0.0.0.0", port=8080)
