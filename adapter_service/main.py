import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Marketplace Adapter Service", version="1.1")

# (Optional but helps Swagger “Failed to fetch” issues)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Provider A: MOCK "ebay"
# -------------------------
MOCK_EBAY = {
    "EBAY-1": ("Gaming Laptop", 899.99, "EUR", True, "https://example.com/ebay-1"),
    "EBAY-2": ("Noise Cancelling Headphones", 249.00, "EUR", False, "https://example.com/ebay-2"),
    "EBAY-3": ("Smartphone", 399.50, "EUR", True, "https://example.com/ebay-3"),
}

def fetch_ebay_mock(external_id: str) -> dict:
    title, price, currency, in_stock, url = MOCK_EBAY.get(
        external_id,
        ("Unknown Item", 1000.0, "EUR", True, None),
    )
    return {
        "marketplace": "ebay",
        "external_id": external_id,
        "title": title,
        "price": price,
        "currency": currency,
        "in_stock": in_stock,
        "url": url,
    }

# -------------------------
# Provider B: REAL HTTP "dummyjson"
# -------------------------
DUMMYJSON_BASE = "https://dummyjson.com/products"

def fetch_dummyjson(external_id: str) -> dict:
    # Accept "DUMMY-1" or just "1"
    if "-" in external_id:
        _, tail = external_id.split("-", 1)
        product_id = int(tail)
    else:
        product_id = int(external_id)

    r = requests.get(f"{DUMMYJSON_BASE}/{product_id}", timeout=10)
    r.raise_for_status()
    p = r.json()

    return {
        "marketplace": "dummyjson",
        "external_id": f"DUMMY-{product_id}",
        "title": p.get("title"),
        "price": float(p.get("price", 0)),
        "currency": "USD",
        "in_stock": bool(p.get("stock", 1) > 0),
        "url": f"{DUMMYJSON_BASE}/{product_id}",
    }

# -------------------------
# One endpoint, multiple providers
# -------------------------
@app.get("/marketplace/price-stock")
def get_price_stock(
    marketplace: str = Query(..., examples=["ebay", "dummyjson"]),
    external_id: str = Query(..., examples=["EBAY-1", "DUMMY-1"]),
):
    m = marketplace.lower().strip()

    if m == "ebay":
        return fetch_ebay_mock(external_id)

    if m == "dummyjson":
        try:
            return fetch_dummyjson(external_id)
        except ValueError:
            return {"error": "For marketplace=dummyjson use external_id like DUMMY-1 (or just 1)."}
        except requests.HTTPError:
            return {"error": "DummyJSON product not found (try DUMMY-1, DUMMY-2, etc.)."}
        except requests.RequestException:
            return {"error": "Network error calling DummyJSON."}

    return {"error": "Unsupported marketplace. Use 'ebay' or 'dummyjson'."}
