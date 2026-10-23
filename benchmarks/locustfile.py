from locust import HttpUser, task


class CountriesUser(HttpUser):
    """One fake user. Every request below is a GET on our own local server."""

    @task(3)
    def list_all(self):
        self.client.get("/countries", name="GET /countries")

    @task(2)
    def filter_by_region(self):
        self.client.get("/countries?region=Asia", name="GET /countries?region=Asia")

    @task(3)
    def one_country(self):
        self.client.get("/countries/IN", name="GET /countries/IN")
