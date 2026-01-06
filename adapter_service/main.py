from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI(title="Marketplace Adapter Service", version="1.0")

# Mock catalog: external_id -> (title, price, currency, in_stock, url)
MOCK = {
    "EBAY-1": ("Gaming Laptop", 899.99, "EUR", True, "https://example.com/ebay-1"),
    "EBAY-2": ("Noise Cancelling Headphones", 249.00, "EUR", False, "https://example.com/ebay-2"),
    "EBAY-3": ("Smartphone", 399.50, "EUR", True, "https://example.com/ebay-3"),
}


@app.get("/marketplace/price-stock")
def get_price_stock(
    marketplace: str = Query(..., examples=["ebay"]),
    external_id: str = Query(..., examples=["EBAY-1"]),
):
    if marketplace.lower() != "ebay":
        return {"error": "Only marketplace='ebay' is supported in mock mode."}

    title, price, currency, in_stock, url = MOCK.get(
        external_id,
        ("Unknown Item", 1000.0, "EUR", True, None),
    )

    return {
        "marketplace": marketplace.lower(),
        "external_id": external_id,
        "title": title,
        "price": price,
        "currency": currency,
        "in_stock": in_stock,
        "url": url,
    }
