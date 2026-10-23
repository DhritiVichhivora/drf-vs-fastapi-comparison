from rest_framework import serializers


class CountrySerializer(serializers.Serializer):
    code = serializers.RegexField(r"^[A-Z]{2}$", help_text="2-letter code, e.g. IN")
    name = serializers.CharField(min_length=2)
    region = serializers.CharField(min_length=1)
    population = serializers.IntegerField(min_value=0)
    capital = serializers.CharField(required=False, allow_null=True)
    flag = serializers.CharField(required=False, allow_null=True)