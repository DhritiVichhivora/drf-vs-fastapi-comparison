import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Load the cached data once, when the server starts
DATA_FILE = Path(__file__).resolve().parent.parent / "shared" / "countries.json"
with open(DATA_FILE, encoding="utf-8") as f:
    countries = json.load(f)

app = FastAPI(title="Countries API (FastAPI)")


class Country(BaseModel):
    code: str = Field(pattern=r"^[A-Z]{2}$", description="2-letter code, e.g. IN")
    name: str = Field(min_length=2)
    region: str = Field(min_length=1)
    population: int = Field(ge=0)
    capital: Optional[str] = None
    flag: Optional[str] = None


@app.get("/countries", response_model=list[Country])
def list_countries(region: Optional[str] = None, search: Optional[str] = None):
    result = countries
    if region:
        result = [c for c in result if c["region"].lower() == region.lower()]
    if search:
        result = [c for c in result if search.lower() in c["name"].lower()]
    return result


@app.get("/countries/{code}", response_model=Country)
def get_country(code: str):
    for c in countries:
        if c["code"].lower() == code.lower():
            return c
    raise HTTPException(status_code=404, detail="Country not found")


@app.post("/countries", response_model=Country, status_code=201)
def create_country(country: Country):
    if any(c["code"] == country.code for c in countries):
        raise HTTPException(status_code=409, detail="Country code already exists")
    countries.append(country.model_dump())
    return country