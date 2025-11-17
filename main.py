import os
from typing import List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

app = FastAPI(title="Party Planner API", description="Backend for Parties, Guests, and Menu items")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Helpers
# -----------------------------
class PartyCreate(BaseModel):
    name: str
    date: Optional[str] = None
    theme: Optional[str] = None
    location: Optional[str] = None
    budget: Optional[float] = None
    notes: Optional[str] = None


def serialize_doc(doc: dict) -> dict:
    """Convert Mongo ObjectId to string and return clean dict"""
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d


# -----------------------------
# Basic endpoints
# -----------------------------
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# -----------------------------
# Parties endpoints
# -----------------------------
@app.get("/api/parties")
def list_parties() -> List[dict]:
    docs = get_documents("party", {}, limit=100)
    return [serialize_doc(d) for d in docs]


@app.post("/api/parties", status_code=201)
def create_party(party: PartyCreate) -> dict:
    party_id = create_document("party", party.model_dump())
    # Return newly created payload with id
    doc = db["party"].find_one({"_id": db["party"].find_one({"_id": db["party"].find_one})})
    # Fallback: just echo the created id + payload
    result = party.model_dump()
    result["id"] = party_id
    return result


@app.get("/api/parties/{party_id}")
def get_party(party_id: str) -> dict:
    from bson import ObjectId
    try:
        doc = db["party"].find_one({"_id": ObjectId(party_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid party id")
    if not doc:
        raise HTTPException(status_code=404, detail="Party not found")
    return serialize_doc(doc)


# -----------------------------
# Guests endpoints (read-only for now)
# -----------------------------
@app.get("/api/parties/{party_id}/guests")
def list_guests(party_id: str) -> List[dict]:
    docs = get_documents("guest", {"party_id": party_id}, limit=500)
    return [serialize_doc(d) for d in docs]


# -----------------------------
# Menu endpoints (read-only for now)
# -----------------------------
@app.get("/api/parties/{party_id}/menu")
def list_menu(party_id: str) -> List[dict]:
    docs = get_documents("menuitem", {"party_id": party_id}, limit=500)
    return [serialize_doc(d) for d in docs]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
