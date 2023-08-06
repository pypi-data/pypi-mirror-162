from asyncore import read
from rest_framework import serializers
from .models import TransitionManager , workevents , workflowitems , Action
from django.conf import settings
from django.apps import apps


class Workeventsserializer(serializers.ModelSerializer):
    event_user = serializers.SlugRelatedField(read_only=True, slug_field = 'email' or 'id')
    class Meta:
        model = workevents
        fields = [
            'id',
            'action',
            'subaction',
            'initial_state',
            'interim_state',
            'final_state',
            'event_user',
            'from_party',
            'to_party'
        ]




class Workitemserializer(serializers.ModelSerializer):
    WorkFlowEvents = Workeventsserializer(many=True, read_only=True)
    event_user = serializers.SlugRelatedField(read_only=True, slug_field = 'email' or 'id')
    class Meta:
        model = workflowitems
        fields = [
            'id',
            'transitionmanager',
            'initial_state',
            'interim_state',
            'final_state',
            'event_user',
            'current_from_party',
            'current_to_party',
            'WorkFlowEvents',
        ]




class TransitionManagerserializer(serializers.ModelSerializer):
    workflowitems = Workitemserializer(read_only = True)
    model = serializers.SerializerMethodField()
    wf_item_id = serializers.SerializerMethodField()
    class Meta:
        model = TransitionManager
        fields = [
            'id',
            'type',
            't_id',
            'wf_item_id',
            'model',
            'workflowitems'
        ]

    def get_model(self,obj):
        try:
            arr = settings.FINFLO['WORK_MODEL']
            for i in arr:
                user = apps.get_model(i)
                qs = user.objects.filter(id = obj.t_id ).values()
                if qs.exists():
                    break
            return qs
        except:
            return None
                    

    def get_wf_item_id(self,obj):
        return obj.workflowitems.id



class Actionseriaizer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = '__all__'



class workflowitemslistserializer(serializers.ModelSerializer):
    class Meta:
        model = workflowitems
        fields = '__all__'


class workeventslistserializer(serializers.ModelSerializer):
    class Meta:
        model = workevents
        fields = '__all__'