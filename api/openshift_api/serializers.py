from rest_framework import serializers
from openshift_api.models.cluster import OpenshiftCluster
from openshift_base.models.package import Package
from openshift_client.models import Project

__all__ = [
    'OpenshiftClusterSerializer',
]


class OpenshiftClusterSerializer(serializers.ModelSerializer):
    package = serializers.SlugRelatedField(
        queryset=Package.objects.all(), slug_field='name', required=False
    )

    class Meta:
        model = OpenshiftCluster
        fields = ['id', 'name', 'package', 'template', 'comment', 'date_created', 'auth']
        read_only_fields = ['id', 'date_created']


class ClusterConfigSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=128)
    value = serializers.JSONField()


class OpenshiftProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']
