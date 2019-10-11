from rest_framework import serializers, viewsets

from .models import Client, EventParam, LogEvent


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['client_platform', 'client_version', 'client_hash']


class ClientHashSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['client_hash']


class EventParamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventParam
        fields = ['param_name', 'param_value']


class LogEventSerializer(serializers.ModelSerializer):
    params = EventParamSerializer(many=True)

    class Meta:
        model = LogEvent
        fields = ['event_name', 'event_time', 'params', 'client']

    def create(self, validated_data):
        params = [EventParam(**item) for item in validated_data["params"]]
        del (validated_data["params"])
        event = LogEvent(**validated_data)
        event.save()
        for param in params:
            param.event = event
            param.save()
        return event


class LogEventViewSet(viewsets.ModelViewSet):
    queryset = LogEvent.objects.all()
    serializer_class = LogEventSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
