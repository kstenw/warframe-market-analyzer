from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from . import db


app = FastAPI(title="Warframe Market Analyzer API")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173"],
	allow_credentials=True,
	allow_methods=["GET"],
	allow_headers=["*"],
)


def serialize_row(row):
	"""Convert database values into JSON-friendly values."""
	if row is None:
		return None

	result = dict(row)
	for key, value in result.items():
		if hasattr(value, "__float__") and not isinstance(value, (int, float)):
			result[key] = float(value)
		elif isinstance(value, datetime):
			result[key] = value.isoformat()
	return result


@app.get("/api/health")
def health():
	return {"status": "ok"}


@app.get("/api/items")
def items(
	search: str = "",
	sort: str = Query("name", pattern="^(name|ducats|price|updated)$"),
	order: str = Query("asc", pattern="^(asc|desc)$"),
	limit: int = Query(50, ge=1, le=200),
	offset: int = Query(0, ge=0),
):
	rows = db.get_prime_parts(search, sort, order, limit, offset)
	return {
		"items": [serialize_row(row) for row in rows],
		"total": db.count_prime_parts(search),
		"limit": limit,
		"offset": offset,
		"lastUpdated": serialize_row({"value": db.get_latest_price_timestamp()})["value"],
	}


@app.get("/api/items/{slug}")
def item_detail(slug: str):
	row = db.get_prime_part(slug)
	if row is None:
		raise HTTPException(status_code=404, detail="Item not found")

	item = serialize_row(row)
	item["marketUrl"] = f"https://warframe.market/items/{slug}"
	return item


@app.get("/api/items/{slug}/history")
def item_history(slug: str, days: int = Query(30, ge=1, le=90)):
	if db.get_prime_part(slug) is None:
		raise HTTPException(status_code=404, detail="Item not found")

	return {
		"slug": slug,
		"days": days,
		"history": [serialize_row(row) for row in db.get_hourly_price_trend(slug, days)],
	}


@app.get("/api/analytics/best-buys")
def best_buys(
	days: int = Query(30, ge=1, le=90),
	limit: int = Query(20, ge=1, le=100),
):
	return {
		"days": days,
		"items": [
			serialize_row(row)
			for row in db.get_best_items_to_buy(days=days, limit=limit)
		],
	}


@app.get("/api/analytics/market-hours")
def market_hours(
	days: int = Query(30, ge=1, le=90),
	min_items: int = Query(10, ge=1),
):
	return {
		"days": days,
		"hours": [
			serialize_row(row)
			for row in db.get_best_market_hours(days=days, min_items=min_items)
		],
	}


@app.get("/api/status")
def status():
	latest = db.get_latest_price_timestamp()
	return {
		"lastSuccessfulCollection": latest.isoformat() if latest else None,
		"collectorStatus": "unknown" if latest is None else "available",
	}