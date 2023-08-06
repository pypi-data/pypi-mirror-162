from rest_framework import routers

from weni.internal.projects.views import TemplateProjectViewSet


router = routers.DefaultRouter()
router.register(r"template-projects", TemplateProjectViewSet, basename="template-projects")


urlpatterns = router.urls
