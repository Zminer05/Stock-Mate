from pydantic import BaseModel


class StockCreate(BaseModel):
    ticker: str
    company_name: str | None = None