# How it works (text for the report, goes with docs/flowchart.png)

## A. One-time setup
1. `shared/fetch_countries.py` reads our REST Countries API key from the `.env` file (the key is never committed to GitHub).
2. It calls the REST Countries v5 API, 100 countries per page, until it has them all.
3. It skips the few territories that have no ISO country code (Abkhazia, Northern Cyprus, Somaliland, South Ossetia), because they would fail our validation rule.
4. It flattens each record into six simple fields (`code`, `name`, `region`, `population`, `capital`, `flag`) and saves 250 countries to `shared/countries.json`. We fetch only once and cache the result, which respects the API's rate limits and keeps the benchmark about the frameworks and not the network.
5. When the FastAPI app or the DRF app starts, it loads that file into an in-memory Python list. There is no database.

## B. What happens to every request
1. A client (the Swagger docs page, a browser, or Locust during the benchmark) sends an HTTP request.
2. The web server receives it. FastAPI runs on uvicorn. DRF runs on waitress (or on uvicorn, which we also tested).
3. The router matches the URL and the method. In FastAPI the decorators `@app.get` and `@app.post` do this. In DRF, `urls.py` points to an `APIView` class.
4. Then one of three things happens:
   - **GET /countries:** the app filters the list by `?region=` and `?search=` if they were given, converts the records to JSON (Pydantic in FastAPI, a serializer in DRF), and returns **200 OK**.
   - **GET /countries/{code}:** the app looks for the code in the list. If found, it returns **200 OK** with that country. If not, it returns **404 Not Found** ("Country not found").
   - **POST /countries:** the app validates the request body (a Pydantic model in FastAPI, `CountrySerializer` in DRF). The rules are: code = two capital letters, name at least 2 characters, population 0 or more. If the data is invalid, it returns an error that lists each wrong field: **422** in FastAPI, **400** in DRF. If it is valid, the app checks whether the code already exists. If it does, it returns **409 Conflict**. If not, it adds the country to the list and returns **201 Created**.
5. The response goes back to the client.

## What differs between the two frameworks
- **Validation:** FastAPI uses Pydantic type hints and returns 422 with a detailed list (type, location, message, input). DRF uses a serializer class and returns 400 with a simple list of messages per field.
- **Docs:** FastAPI generates the `/docs` page by itself. DRF needed the extra package `drf-spectacular` and some extra decorators.
- **Code size:** FastAPI is one file of 48 lines. DRF is five files of about 93 lines.
