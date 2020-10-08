#!/env/python3
# -*- coding: utf-8 -*-

from rest_framework import serializers, validators
from django.db import transaction

from activities.models import Activity, MetadataOption, ActivityTranslation, AuthorInstitution
from institutions.serializers.institutions import PersonSerializer, InstitutionSerializer


class MetadataOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadataOption
        exclude = ["id"]
        validators = []


class ActivityTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityTranslation
        exclude = ['master']

class AuthorInstitutionSerializer(serializers.ModelSerializer):
    author = PersonSerializer()
    institution = InstitutionSerializer(required=False, allow_null=True)
    #activity = ActivitySerializer()

    class Meta:
        model = AuthorInstitution
        exclude = ('id', 'activity')
        validators = []

    def create(self, validated_data):
        print('AuthorInstitutionSerializer.create')
        return super().create(validated_data)

    def validate(self, attrs):
        print('AuthorInstitutionSerializer.validate')
        return super().validate(attrs)


class ActivitySerializer(serializers.ModelSerializer):
    age = MetadataOptionSerializer(many=True)
    level = MetadataOptionSerializer(many=True)
    time = MetadataOptionSerializer()
    group = MetadataOptionSerializer(allow_null=True)
    supervised = MetadataOptionSerializer(allow_null=True)
    cost = MetadataOptionSerializer(allow_null=True)
    location = MetadataOptionSerializer(allow_null=True)
    skills = MetadataOptionSerializer(many=True)
    learning = MetadataOptionSerializer()
    translations = ActivityTranslationSerializer(many=True)
    authors = AuthorInstitutionSerializer(many=True, required=False)

    class Meta:
        model = Activity
        exclude = ["id"]
        # validators = []

    def validate_code(self, value):
        print('validate code')
        if not value:
            raise serializers.ValidationError('code is missing')
        return value

    def validate(self, attrs):
        print('validate activity')
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        print('Create activity')
        age = validated_data.pop('age')
        level = validated_data.pop('level')
        time = validated_data.pop('time')
        group = validated_data.pop('group')
        supervised = validated_data.pop('supervised')
        cost = validated_data.pop('cost')
        location = validated_data.pop('location')
        skills = validated_data.pop('skills')
        learning = validated_data.pop('learning')
        translations = validated_data.pop('translations')
        authors = validated_data.pop('authors')

        activity = Activity(**validated_data)

        if time:
            activity.time = MetadataOption.objects.get_or_create(**time)[0]

        if group:
            activity.group = MetadataOption.objects.get_or_create(**group)[0]

        if supervised:
            activity.supervised = MetadataOption.objects.get_or_create(**supervised)[0]

        if cost:
            activity.cost = MetadataOption.objects.get_or_create(**cost)[0]

        if location:
            activity.location = MetadataOption.objects.get_or_create(**location)[0]

        if learning:
            activity.learning = MetadataOption.objects.get_or_create(**learning)[0]

        activity.save()

        for age_item in age:
            activity.age.add(MetadataOption.objects.get_or_create(**age_item)[0])

        for level_item in level:
            activity.level.add(MetadataOption.objects.get_or_create(**level_item)[0])

        for skills_item in skills:
            activity.skills.add(MetadataOption.objects.get_or_create(**skills_item)[0])

        for author in authors:
            author.update(activity=activity)
            activity.authors.add(AuthorInstitution.objects.get_or_create(**author)[0])

        activity.save()

        for translation in translations:
            translation.update(master=activity)
            t = ActivityTranslation(**translation)
            t.save()

        return activity

    def update(self, instance, validated_data):
        print('updating activity')


class UnaweActivitySerializer(serializers.ModelSerializer):
    time = MetadataOptionSerializer()
    group = MetadataOptionSerializer()
    learning = MetadataOptionSerializer()
    age = MetadataOptionSerializer()
    level = MetadataOptionSerializer()
    skills = MetadataOptionSerializer()

    class Meta:
        model = Activity
        fields = "__all__"

    def to_internal_value(self, data):
        data.update(code=data['uuid'])
        return super().to_internal_value(data)


