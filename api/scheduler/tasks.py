# 定时同步任务
import logging
import _thread
import time
import uuid

from celery import shared_task
from celery_api.utils import register_as_period_task
from openshift_api.models.cluster import OpenshiftCluster
from openshift_client.models import Cluster

logger = logging.getLogger(__name__)


@shared_task
@register_as_period_task(interval=20)
def sync_connect_config():
    clusters = OpenshiftCluster.objects.filter(OpenshiftCluster.OPENSHIFT_STATUS_RUNNING)
    logger.info('当前运行OPENSHIFT集群数量： {}'.format(len(clusters)))
    if clusters:
        logger.info('开始同步集群集群信息...')
    else:
        logger.info('不存在运行的OPENSHIFT集群,取消同步集群信息...')
    for cluster in clusters:
        sync_cluster_info.apply_async(
            args=(cluster,), task_id=str(uuid.uuid4())
        )
    logger.info('同步集群信息完毕！')


@shared_task
def sync_cluster_info(cluster):
    get_cluster_connection_config()
    get_node_heart_beat()


def get_cluster_connection_config(cluster):
    logger.info('开始同步集群:{} 连接信息......'.format(cluster.name))
    cluster.get_connect_config()
    logger.info('完成同步集群:{} 连接信息......'.format(cluster.name))


def get_node_heart_beat(cluster):
    logger.info('开始获取集群:{} 节点心跳信息......'.format(cluster.name))
    cluster = Cluster.objects.get(cluster.id)
    cluster.get_node_heartbeat()
    logger.info('完成获取集群:{} 节点心跳信息......'.format(cluster.name))


@shared_task
def get_cluster_info(cluster):
    logger.info('开始获取集群:{} 资源信息......'.format(cluster.name))
    logger.info('完成获取集群:{} 资源信息......'.format(cluster.name))


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


def node_health_check():
    pass


def cluster_health_check():
    pass
