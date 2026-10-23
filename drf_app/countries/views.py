import json
from pathlib import Path

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CountrySerializer

# Load the cached data once, when the server starts
DATA_FILE = Path(__file__).resolve().parent.parent.parent / "shared" / "countries.json"
with open(DATA_FILE, encoding="utf-8") as f:
    countries = json.load(f)


class CountryList(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter("region", str, required=False),
            OpenApiParameter("search", str, required=False),
        ],
        responses=CountrySerializer(many=True),
    )
    def get(self, request):
        result = countries
        region = request.query_params.get("region")
        search = request.query_params.get("search")
        if region:
            result = [c for c in result if c["region"].lower() == region.lower()]
        if search:
            result = [c for c in result if search.lower() in c["name"].lower()]
        return Response(CountrySerializer(result, many=True).data)

    @extend_schema(request=CountrySerializer, responses={201: CountrySerializer})
    def post(self, request):
        serializer = CountrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # sends 400 with errors if invalid
        if any(c["code"] == serializer.validated_data["code"] for c in countries):
            return Response(
                {"detail": "Country code already exists"}, status=status.HTTP_409_CONFLICT
            )
        countries.append(dict(serializer.validated_data))
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CountryDetail(APIView):
    @extend_schema(responses=CountrySerializer)
    def get(self, request, code):
        for c in countries:
            if c["code"].lower() == code.lower():
                return Response(CountrySerializer(c).data)
        return Response({"detail": "Country not found"}, status=status.HTTP_404_NOT_FOUND)