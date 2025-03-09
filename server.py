import json
import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel

BUILD = 2
VERSION = "1.0"

# env
load_dotenv()
TOKEN = os.getenv("TALLYBOX_API_TOKEN", None)
VALID_API_GET_TOTAL_TOKEN = os.getenv("TALLYBOX_API_GET_TOTAL_TOKEN", default=TOKEN)
VALID_API_GET_HISTORY_TOKEN = os.getenv("TALLYBOX_API_GET_HISTORY_TOKEN", default=TOKEN)
VALID_API_SET_TOKEN = os.getenv("TALLYBOX_API_SET_TOKEN", default=TOKEN)
BF_DATA_DIR_PATH = os.getenv("TALLYBOX_DATA_DIR_PATH")

missing_vars = []
if BF_DATA_DIR_PATH is None:
    missing_vars.append("[TALLYBOX_DATA_DIR_PATH]")
if VALID_API_GET_TOTAL_TOKEN is None:
    missing_vars.append("[TALLYBOX_API_GET_TOTAL_TOKEN or TALLYBOX_API_TOKEN]")
if VALID_API_GET_HISTORY_TOKEN is None:
    missing_vars.append("[TALLYBOX_API_GET_HISTORY_TOKEN or TALLYBOX_API_TOKEN]")
if VALID_API_SET_TOKEN is None:
    missing_vars.append("[TALLYBOX_API_SET_TOKEN or TALLYBOX_API_TOKEN]")


if missing_vars:
    raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

BF_DATA_TOTAL_FILE = f"{BF_DATA_DIR_PATH}/total.txt"
BF_DATA_HISTORY_FILE = f"{BF_DATA_DIR_PATH}/history.json"
BF_DATA_VERSION_FILE = f"{BF_DATA_DIR_PATH}/version.txt"

def set_ver():
    with open(BF_DATA_VERSION_FILE, 'w') as f:
        f.write("tallybox:{BUILD}")

set_ver()

class BuckwheatData:
    def __init__(self, total, history):
        self.total = total
        self.history = history

    def save(self):
        with open(BF_DATA_TOTAL_FILE, 'w') as f:
            f.write(str(self.total))

        with open(BF_DATA_HISTORY_FILE, 'w') as f:
            f.write(json.dumps(self.history))

def load() -> BuckwheatData:
    _total = 0
    _history = []
    c = 2
    if os.path.exists(BF_DATA_TOTAL_FILE):
        with open(BF_DATA_TOTAL_FILE, 'r') as f:
            _total = int(str(f.read()))
        c -= 1

    if os.path.exists(BF_DATA_HISTORY_FILE):
        with open(BF_DATA_HISTORY_FILE, 'r') as f:
            _history = json.loads(str(f.read()))
        c -= 1

    obj = BuckwheatData(_total, _history)
    if c > 0:
        obj.save()
    return obj

# api
app = FastAPI()
security = HTTPBearer()
data = load()


def verify_token(token: str, expected_token: str) -> bool:
    return token == expected_token

def throw_if_token_bad(token, expected):
    if not verify_token(token.credentials, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/total")
async def get_total(token = Depends(security)):
    throw_if_token_bad(token, VALID_API_GET_TOTAL_TOKEN)
    return {"total": data.total}

@app.get("/history")
async def get_history(token = Depends(security)):
    """Get total amount of money"""
    throw_if_token_bad(token, VALID_API_GET_HISTORY_TOKEN)
    return {"history": data.history}

@app.get("/data")
async def get_data(token = Depends(security)):
    throw_if_token_bad(token, VALID_API_SET_TOKEN)
    return {"history": data.history, "total": data.total}

class ChangeRequest(BaseModel):
    amount: float
    comment: str

@app.post("/change")
async def post_change(request: ChangeRequest, token = Depends(security)):
    throw_if_token_bad(token, VALID_API_SET_TOKEN)
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
