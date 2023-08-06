from rest_framework.mixins import CreateModelMixin

from weni.internal.views import InternalGenericViewSet
from weni.internal.projects.serializers import TemplateProjectSerializer


class TemplateProjectViewSet(CreateModelMixin, InternalGenericViewSet):
    serializer_class = TemplateProjectSerializer
