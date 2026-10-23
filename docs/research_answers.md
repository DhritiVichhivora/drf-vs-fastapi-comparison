## Question 1: What is the difference between synchronous and asynchronous programming?

Synchronous programming executes tasks one by one, waiting for each task to finish before moving to the next. Asynchronous programming allows the server to handle other requests while waiting for tasks like database queries or external API calls to complete.

In our project, we used normal `def` functions, so we did not implement asynchronous programming. Our data is already in memory, so there was nothing to wait for, which is why async would not have helped much here. FastAPI was most likely faster because it does less work per request, not because of async. We measured approximately 762 requests per second with FastAPI, compared to 393 with DRF on Waitress. DRF on uvicorn did even worse (about 111 requests per second), because DRF is synchronous code running on a server built for async code. Waitress is built for synchronous code, which is why DRF did better there.

## Question 2: How does each framework validate data?

FastAPI uses Pydantic models and Python type hints to validate incoming data automatically, with constraints such as Field(ge=0). These models also generate the interactive /docs page. In contrast, Django REST Framework (DRF) uses serializers with fields such as IntegerField(min_value=0), where the view explicitly calls is_valid() to validate the input.

In our project, both frameworks implemented the same validation rules: the country code had to consist of two uppercase letters, the name had to contain at least two characters, and the population had to be non-negative. However, their error responses differed. FastAPI returned a 422 status code with detailed information, including the error type, location, message, and input value. DRF returned a 400 status code with simpler, field-specific error messages.

## Question 3: When would you choose FastAPI or Django REST Framework?

I would choose FastAPI for lightweight, high-performance APIs and microservices where speed, simplicity, and automatic API documentation are important. In our project, FastAPI required only one file with 48 lines of code and achieved approximately 762 requests per second.

I would choose Django REST Framework (DRF) for larger applications that need Django's ORM, built-in admin panel, authentication, permissions, and extensive ecosystem. In our project, DRF required five files with around 93 lines of code and achieved 393 requests per second using Waitress. Part of those extra lines is the code we added for DRF's documentation page.

Our numbers come from one laptop and one test setup, so they compare the two frameworks under the same conditions and do not predict production performance.

In short: if a project needs a database, an admin panel and login out of the box, choose DRF. If it is a small, fast API, choose FastAPI.
