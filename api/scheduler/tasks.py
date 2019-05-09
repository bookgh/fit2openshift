# 定时同步任务
import logging
from celery import shared_task
from openshift_api.models.cluster import OpenshiftCluster
from openshift_client.models import Cluster

logger = logging.getLogger(__name__)


def sync_cluster_config():
    running_clusters = OpenshiftCluster.objects.filter(status=OpenshiftCluster.OPENSHIFT_STATUS_RUNNING)
    for cluster in running_clusters:
        logger.info('sync connect config ' + cluster.name)
        cluster.get_connect_config()


def sync_cluster_info():
    running_clusters = Cluster.objects.filter(status=OpenshiftCluster.OPENSHIFT_STATUS_RUNNING)
    for cluster in running_clusters:
        logger.info('sync cluster info ' + cluster.name)
        cluster.sync_projects()
        cluster.sync_pod()
        cluster.sync_services()


@shared_task
def test_sync():
    print('test')
