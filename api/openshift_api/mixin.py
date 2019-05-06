import uuid

from django.db import models

from ansible_api.api.mixin import ProjectResourceAPIMixin


class ClusterResourceAPIMixin(ProjectResourceAPIMixin):
    lookup_kwargs = 'cluster_name'


class OpenshiftClusterResourceManager(models.Manager):
    def get_queryset(self):
        queryset = super(OpenshiftClusterResourceManager, self).get_queryset()
        if not current_project:
            return queryset
        if current_project.is_real():
            queryset = queryset.filter(project=current_project.id)
        return queryset

    def create(self, **kwargs):
        if 'project' not in kwargs and current_project.is_real():
            kwargs['project'] = current_project._get_current_object()
        return super().create(**kwargs)

    def all(self):
        if current_project:
            return super().all()
        else:
            return self

    def set_current_org(self, project):
        set_current_project(project)
        return self
