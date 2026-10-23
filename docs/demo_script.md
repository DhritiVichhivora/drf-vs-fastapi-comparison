Part 1: Introduction and goal (Dhriti, 1 minute)
Screen: GitHub README.
SAY: "Hello. We are Dhriti, Tanvi, Navya and Shreeya. Our topic is Django REST Framework versus FastAPI. Both are Python tools for building APIs. We built the same small countries API in both, using data from the REST Countries API, and compared them on code size, speed, validation, and the documentation each one generates. Both apps have the same three endpoints: list countries, get one country by its code, and add a country."
Scroll slowly to the "Members and roles" table so the teacher sees the roles.
Part 2: Flowchart and how it works (Dhriti, 1 minute 30 seconds)
Screen: flowchart.png. Zoom in if it is small.
1.	Point at Part A at the top. "First, a script downloads the countries once from the API using our key, which is kept out of GitHub. It skips four territories with no country code, and saves 250 countries into a JSON file. Both apps load that file into memory."
2.	Point at Part B. "For every request: the client sends a request, the server receives it (uvicorn for FastAPI, waitress for DRF), and the router sends it to the right function."
3.	Follow the three branches with your finger: "A GET for the list returns 200. A GET for one country returns 200 or 404. A POST is validated first: wrong data gives 422 in FastAPI or 400 in DRF, a duplicate gives 409, and a good one gives 201 Created."
SAY: "The flowchart is the same for both apps. The difference is how each framework does each step, and that is what we compare."
Part 3: FastAPI live demo (Tanvi, 2 minutes 30 seconds)
Screen: FastAPI docs tab (http://127.0.0.1:8000/docs).
1.	Say: "This page was created automatically by FastAPI. We did not write any documentation code. It lists our three endpoints."
2.	Click GET /countries, then Try it out. Type Asia in region, click Execute. Say: "Status 200 and a list of Asian countries, filtered by region."
3.	Click GET /countries/{code}, Try it out. Type IN, Execute. Say: "India, status 200."
4.	Change the code to ZZ and Execute. Say: "No such country, so we get 404 Not Found."
5.	Click POST /countries, Try it out. Replace the body with the wrong data below and Execute. Say: "Now invalid data: a bad code, a one-letter name, and a negative population. FastAPI answers 422 and lists every mistake, with the type, location, message and the value we sent."
6.	Replace the body with the good data below and Execute. Say: "Valid data, so 201 Created."
7.	Click Execute again with the same body. Say: "The code already exists, so we get 409 Conflict."
Wrong data:
{"code": "xx1", "name": "T", "region": "Asia", "population": -5}

Good data:
{"code": "ZZ", "name": "Testland", "region": "Asia", "population": 1000}

SAY: "All of this validation comes from one Pydantic class of about ten lines. FastAPI used the same class for validation, the response format and this docs page."
If time allows, switch to the code window and show the Country class in fastapi_app/main.py.
Part 4: DRF live demo (Navya, 2 minutes)
Screen: DRF docs tab (http://127.0.0.1:8001/docs/).
1.	Say: "This is the same API built with Django REST Framework. This docs page needed an extra package called drf-spectacular, plus some decorators in our code."
2.	Click GET /countries, Try it out, region Asia, Execute. Say: "Same result, status 200."
3.	Click GET /countries/{code}, code IN, Execute. Say: "India, 200."
4.	Code ZZ, Execute. Say: "404 Not Found, same as FastAPI."
5.	Click POST /countries, Try it out. Paste the wrong data (same as above) and Execute. Say: "Same wrong data. DRF returns 400 Bad Request, not 422, with a simpler list of messages per field. The same three mistakes were found."
6.	Point at the documented responses on the page. Say: "In the FastAPI docs, 422 was listed automatically. Here, 400 and 404 show as Undocumented unless we declare them."
SAY: "So both frameworks enforce the same rules. The differences are the status code, the detail of the message, and how much work it takes to get the docs."
Optional if you have time: show the DRF files (serializers.py, views.py) and say "DRF splits the work into separate files: serializer, view and URLs, while FastAPI did everything in one file."
Part 5: Results, speed and code size (Shreeya, 1 minute 45 seconds)
Screen: benchmark_charts.png, then the README code size table.
1.	Show the chart. Say: "We tested speed with Locust: 50 simulated users for 30 seconds, repeated 3 times per setup, one server at a time. We tested three setups."
2.	Point at each bar: "FastAPI handled 762 requests per second. DRF on waitress, its usual server, handled 393. DRF on uvicorn handled only 111, because DRF is synchronous code running on a server built for async code. There were no failed requests."
3.	Point at the median and p95 charts: "FastAPI also responded faster: a typical response took 59 milliseconds, against 113 for DRF on waitress."
4.	Scroll the README to the Code size table. Say: "FastAPI needed one file and 48 lines. DRF needed five files and about 93 lines. Part of that is the code that makes the DRF docs page show our filters."
5.	Say the honesty line: "Everything ran on one laptop, so these numbers compare the two fairly but do not predict production speed."
If asked "is FastAPI faster because of async?" answer: "Not in our test. We used normal functions and the data is in memory, so there was nothing to wait for. It was most likely faster because it does less work per request."
Part 6: Conclusion (Dhriti, 45 seconds)
Screen: README.
SAY: "To conclude: for a small, fast API, FastAPI is the better choice. It needed less code, was about twice as fast in our test, and made its docs and validation errors automatically. DRF is the better choice when a project needs what Django already provides, such as a database layer, an admin panel and login. Our project did not use those, so we did not test them. Thank you. We are happy to answer questions."
