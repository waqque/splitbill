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

app = FastAPI(title="Bill Splitter") # create FastAPI app

BASE_DIR = Path(__file__).parent.parent # project root folder 

# connect static files (css, js, images)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# connect templates folde
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# create JSON storage
storage = JSONStorage(BASE_DIR / "data")

# current active bill
current_bill: Optional[Bill] = None

@app.get("/", response_class=HTMLResponse) # main page route
async def index(request: Request):
    # get all saved bills
    bills = storage.list_bills()

    # return html page
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_bill": current_bill,
        "bills": bills
    })

@app.get("/bill/{bill_id}", response_class=HTMLResponse) # route for bill page
async def view_bill(request: Request, bill_id: str):

     # load bill from json file
    bill = storage.load(f"{bill_id}.json")

    # if bill does not exist
    if not bill:
        raise HTTPException(404, "Счёт не найден")

    # calculate debts
    debts = compute_debts(bill)

    # list with usernames instead of ids
    debts_named = []

    # process all debts
    for from_id, to_id, amount in debts:
        from_name = bill.get_user_name(from_id) # get debtor name
        to_name = bill.get_user_name(to_id) # get receiver name
        debts_named.append((from_name, to_name, float(amount))) # add formatted debt

    # return bill page
    return templates.TemplateResponse("bill.html", {
        "request": request,
        "bill": bill,
        "debts": debts_named
    })
@app.post("/create") # route for creating a new bill
async def create_bill(name: str = Form(...)):

    # use global current bill
    global current_bill
    bill = Bill(name=name) # create new bill
    storage.save(bill, f"{bill.id}.json") # save bill to json
    current_bill = bill # set current active bill
    return RedirectResponse("/", status_code=303)# redirect to main page


@app.post("/load/{bill_id}") # route for loading bill
async def load_bill(bill_id: str):

    # use global current bill
    global current_bill
    current_bill = storage.load(f"{bill_id}.json") # load bill from storage
    
    # if bill does not exist
    if not current_bill:
        raise HTTPException(404, "Счёт не найден")
    return RedirectResponse("/", status_code=303) # redirect to main page


@app.post("/close") # route for closing current bill
async def close_bill(): 
    global current_bill # use global current bill
    current_bill = None # remove current bill
    return RedirectResponse("/", status_code=303) # redirect to main page