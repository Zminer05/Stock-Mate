from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tracked_stock import TrackedStock
from app.schemas.stock import StockCreate

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

    return stocks