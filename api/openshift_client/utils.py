# generate okd client
from openshift.dynamic import DynamicClient
from kubernetes import client, config


def generate_client(connect_config):
    k8s_client = config.new_client_from_config(connect_config)
    return DynamicClient(k8s_client)
