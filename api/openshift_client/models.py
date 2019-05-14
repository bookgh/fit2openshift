import uuid

from django.db import models

from openshift_api.models.cluster import OpenshiftCluster
from openshift_base.models.node import Node
from openshift_client.utils import generate_client

from ansible_api.models.mixins import AbstractProjectResourceModel, AbstractExecutionModel


class Cluster(OpenshiftCluster):
    class Meta:
        proxy = True

    def sync_projects(self):
        api_client = generate_client(self.connect_config)
        project_list = api_client.resources.get(api_version='v1', kind='Project').get()
        projects = []
        for project in project_list.items:
            p = Project.objects.update_or_create(name=project.metadata.name)
            projects.append(p)
        self.projects.set(projects)

    def get_node_heartbeat(self):
        api_client = generate_client(self.connect_config)
        node_list = api_client.resources.get(api_version='v1', kind='Node').get()
        self.change_to()
        nodes = Node.objects.all()
        for node in nodes:
            remote_node = None
            for _node in node_list.items:
                if _node.metadata.name == node.name:
                    remote_node = _node
            # 判断是否存在告警
            if remote_node:
                node_ready_key = 'KubeletReady'
                for condition in remote_node.status.conditions:
                    if condition.reason == node_ready_key:
                        if condition.status:
                            node.status = Node.NODE_STATUS_READY
                        else:
                            node.status = Node.NODE_STATUS_NOT_READY
            node.save()

    def sync_services(self):
        api_client = generate_client(self.connect_config)
        for project in self.projects.all():
            services = []
            service_list = api_client.resources.get(api_version='v1', kind='Service').get(namespace=project.name)
            for service in service_list.items:
                s = Service.objects.update_or_create(name=service.metadata.name, type=service.spec.type,
                                                     cluster_ip=service.spec.clusterIP)
                services.append(s)
            project.services.set(services)
            self.services.set(services)

    def sync_pod(self):
        api_client = generate_client(self.connect_config)
        for project in self.projects.all():
            pods = []
            pod_list = api_client.resources.get(api_version='v1', kind='Pod').get(namespace=project.name)
            for pod in pod_list.items:
                p = Pod(name=pod.metadata.name)
                p.save()
                pods.append(p)
            project.pods.set(pods)
            self.pods.set(pods)


class Pod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)


class Project(AbstractProjectResourceModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    services = models.ManyToManyField('Service')
    pods = models.ManyToManyField('Pod')
    project = models.ForeignKey('ansible_api.Project', on_delete=models.CASCADE)


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=128)
    cluster_ip = models.CharField(max_length=128)


class SyncOpenshiftExecution(AbstractProjectResourceModel, AbstractExecutionModel):
    project = models.ForeignKey('ansible_api.Project', on_delete=models.CASCADE)
