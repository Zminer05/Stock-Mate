from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tracked_stock import TrackedStock
from app.schemas.stock import StockCreate
from app.services.finnhub_service import get_stock_quote

router = APIRouter(prefix="/stocks", tags=["Stocks"])

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_user_id_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except:
        return None


@router.post("/add")
def add_stock(
    stock: StockCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_id = get_user_id_from_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    new_stock = TrackedStock(
        ticker=stock.ticker.upper(),
        company_name=stock.company_name,
        user_id=user_id
    )

    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)

    return {
        "message": "Stock added",
        "stock_id": new_stock.id
    }


@router.get("/my-stocks")
def get_my_stocks(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_id = get_user_id_from_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    stocks = db.query(TrackedStock).filter(
        TrackedStock.user_id == user_id
    ).all()

    stock_data = []

    for stock in stocks:
        live_data = get_stock_quote(stock.ticker)

        stock_data.append({
            "id": stock.id,
            "ticker": stock.ticker,
            "company_name": stock.company_name,
            "current_price": live_data.get("c"),
            "high": live_data.get("h"),
            "low": live_data.get("l"),
            "open": live_data.get("o"),
            "previous_close": live_data.get("pc")
        })

    return stock_data

@router.get("/quote/{ticker}")
def stock_quote(ticker: str):
    data = get_stock_quote(ticker)

    return {
        "ticker": ticker.upper(),
        "current_price": data.get("c"),
        "high": data.get("h"),
        "low": data.get("l"),
        "open": data.get("o"),
        "previous_close": data.get("pc")
    }