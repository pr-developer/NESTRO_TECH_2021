from rest_framework import serializers

from .models import Nodes, Edges

class NodesSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='label_gr')
    id = serializers.CharField(source='id_gr')
    type = serializers.CharField(source='type_gr')

    class Meta:
        model = Nodes
        fields = ('id', 'label',  'type', 'layer', 'access', 'stead', 'costdown', 'coordX', 'coordY', 'RTO', 'RPO')

class NodesViewSerializer(serializers.ModelSerializer):

    text = serializers.CharField(source='label_gr')
    key = serializers.CharField(source='id_gr')
    icon = serializers.CharField(source='layer')
    caption = serializers.CharField(source='label_gr')

    class Meta:
        model = Nodes
        fields = ('key', 'pos', 'icon', 'color', 'text', 'description', 'caption', 'access', 'stead', 'costdown', 'RTO', 'RPO')


class EdgesSerializer(serializers.ModelSerializer):

    id = serializers.CharField(source='id_gr')

    class Meta:
        model = Edges
        fields = ('id', 'source',  'target', 'weight')

class EdgesViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Edges

    def to_representation(self, instance):
        return {
            'from':instance.source,
            'to': instance.target,
            'weight':instance.weight,
            'color':instance.color,
        }
