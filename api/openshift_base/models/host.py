import uuid
from django.db import models
from ansible_api.models.inventory import BaseHost
from ansible_api.models.utils import name_validator
from ansible_api.tasks import run_im_adhoc

__all__ = ['Host', 'HostInfo']


class Host(BaseHost):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    node = models.ForeignKey('Node', default=None, null=True, related_name='node',
                             on_delete=models.SET_NULL)
    name = models.CharField(max_length=128, validators=[name_validator], unique=True)

    @property
    def cluster(self):
        if self.node is not None:
            return self.node.project.name
        else:
            return '无'

    @property
    def info(self):
        return self.infos.all().latest()

    def gather_info(self):
        info = HostInfo.objects.create(host_id=self.id)
        info.gather_info()

    class Meta:
        ordering = ('name',)


class HostInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    memory = models.fields.BigIntegerField(default=0)
    os = models.fields.CharField(max_length=128, default="")
    os_version = models.fields.CharField(max_length=128, default="")
    cpu_core = models.fields.IntegerField(default=0)
    host = models.ForeignKey('Host', on_delete=models.CASCADE, null=True, related_name='infos')
    volumes = models.ManyToManyField('Volume')
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'date_created'

    def gather_info(self):
        host = self.host
        hosts = [self.host.__dict__]
        result = run_im_adhoc(adhoc_data={'pattern': host.name, 'module': 'setup'},
                              inventory_data={'hosts': hosts, 'vars': {}})
        if not result.get('summary', {}).get('success', False):
            raise Exception("get os info failed!")
        else:
            facts = result["raw"]["ok"][host.name]["setup"]["ansible_facts"]
            self.memory = facts["ansible_memtotal_mb"]
            self.cpu_core = facts["ansible_processor_count"]
            self.os = facts["ansible_distribution"]
            self.os_version = facts["ansible_distribution_version"]
            self.save()
            devices = facts["ansible_devices"]
            volumes = []
            for name in devices:
                if not name.startswith(('dm', 'loop', 'sr')):
                    volume = Volume(name='/dev/' + name)
                    volume.size = devices[name]['size']
                    volume.save()
                    volumes.append(volume)
            self.volumes.set(volumes)


class Volume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=128)
    size = models.CharField(max_length=16)

    class Meta:
        ordering = ('size',)
