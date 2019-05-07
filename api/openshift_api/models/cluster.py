import os

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from ansible_api.tasks import run_im_adhoc
from fit2ansible.settings import ANSIBLE_PROJECTS_DIR
from openshift_base.models.cluster import AbstractCluster
from openshift_base.models.node import Node
from openshift_base.models.role import Role

__all__ = ['OpenshiftCluster']


class OpenshiftCluster(AbstractCluster):
    OPENSHIFT_STATUS_UNKNOWN = 'UNKNOWN'
    OPENSHIFT_STATUS_RUNNING = 'RUNNING'
    OPENSHIFT_STATUS_STOP = 'STOP'
    OPENSHIFT_STATUS_INSTALLING = 'INSTALLING'

    OPENSHIFT_STATUS_CHOICES = (
        (OPENSHIFT_STATUS_RUNNING, 'running'),
        (OPENSHIFT_STATUS_STOP, 'stop'),
        (OPENSHIFT_STATUS_INSTALLING, 'installing'),
        (OPENSHIFT_STATUS_UNKNOWN, 'unknown')
    )
    connect_config = models.TextField(null=True, blank=True)
    auth = models.CharField(max_length=128, default=None, null=True, blank=True)
    projects = models.ManyToManyField('openshift_client.Project')
    services = models.ManyToManyField('openshift_client.Service')
    pods = models.ManyToManyField('openshift_client.Pod')
    status = models.CharField(max_length=128, choices=OPENSHIFT_STATUS_CHOICES, default=OPENSHIFT_STATUS_UNKNOWN)

    def get_connect_config(self):
        host = self.group_set.get(name='masters').hosts.first()
        hosts = [host.__dict__]
        src = '/root/.kube/config'
        dest = os.path.join(ANSIBLE_PROJECTS_DIR, self.name, 'config')
        result = run_im_adhoc(
            adhoc_data={'pattern': host.name, 'module': 'fetch',
                        'args': {'src': src, 'dest': dest}},
            inventory_data={'hosts': hosts, 'vars': {}})
        if not result.get('summary', {}).get('success', False):
            raise Exception("get connect config failed!")
        else:
            dest = result["raw"]["ok"][host.name]["fetch"]['dest']
            self.connect_config = dest
            self.save()

    def create_roles(self):
        super().create_roles()
        ose_role = Role.objects.get(name='OSEv3')
        templates = self.package.meta['templates']
        template = Node
        for t in templates:
            if t['name'] == self.template:
                template = t
        private_var = template['private_vars']
        role_vars = ose_role.vars
        role_vars.update(private_var)
        ose_role.vars = role_vars
        ose_role.save()

    def create_node_localhost(self):
        Node.objects.create(
            name="localhost", vars={"ansible_connection": "local"},
            project=self, meta={"hidden": True}
        )

    def configs(self, tp='list'):
        self.change_to()
        role = Role.objects.get(name='OSEv3')
        configs = role.vars
        if tp == 'list':
            configs = [{'key': k, 'value': v} for k, v in configs.items()]
        return configs

    def set_config(self, k, v):
        self.change_to()
        role = Role.objects.select_for_update().get(name='OSEv3')
        _vars = role.vars
        if isinstance(v, str):
            v = v.strip()
        _vars[k] = v
        role.vars = _vars
        role.save()

    def get_config(self, k):
        v = self.configs(tp='dict').get(k)
        return {'key': k, 'value': v}

    def del_config(self, k):
        self.change_to()
        role = Role.objects.get(name='OSEv3')
        _vars = role.vars
        _vars.pop(k, None)
        role.vars = _vars
        role.save()

    def on_cluster_create(self):
        super().on_cluster_create()
        self.create_node_localhost()


@receiver(post_save, sender=OpenshiftCluster)
def on_cluster_save(sender, instance=None, **kwargs):
    if instance and instance.template and kwargs.get('created'):
        instance.on_cluster_create()
