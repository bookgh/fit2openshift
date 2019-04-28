from django.apps import AppConfig
from kubernetes import client, config

class OpenshiftClientConfig(AppConfig):
    name = 'openshift_client'


