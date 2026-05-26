from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from decimal import Decimal
from typing import Optional

from src.models import Bill, User, Item, Payment
from src.storage import JSONStorage
from src.calculator import compute_debts

app = FastAPI(title="Bill Splitter")

BASE_DIR = Path(__file__).parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

storage = JSONStorage(BASE_DIR / "data")
current_bill: Optional[Bill] = None