#!/env/python3
# -*- coding: utf-8 -*-

from rest_framework import serializers
from institutions.models import Location, Institution, Person


class LocationSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        print('LocationSerializer.validate')
        return super().validate(attrs)

    def create(self, validated_data):
        print('LocationSerializer.create')
        return Location.objects.create(**validated_data)

    class Meta:
        model = Location
        exclude = ['id']


class InstitutionSerializer(serializers.ModelSerializer):
    location = LocationSerializer(required=False, allow_null=True)

    def validate(self, attrs):
        print('InstitutionSerializer.validate')
        return super().validate(attrs)

    def create(self, validated_data):
        print('InstitutionSerializer.create')
        return Institution.objects.create(**validated_data)

    class Meta:
        model = Institution
        exclude = ['id']


class PersonSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer(required=False, allow_null=True)

    def validate(self, attrs):
        print('PersonSerializer.validate')
        return super().validate(attrs)

    def create(self, validated_data):
        print('PersonSerializer.create')
        return Person.objects.create(**validated_data)


    class Meta:
        model = Person
        exclude = ['id']

