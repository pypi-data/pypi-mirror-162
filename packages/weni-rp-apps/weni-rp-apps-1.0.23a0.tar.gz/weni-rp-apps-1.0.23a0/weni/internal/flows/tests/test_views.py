from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from temba.flows.models import Flow
from temba.orgs.models import Org
from weni.internal.flows.views import FlowViewSet


User = get_user_model()


class TestSla(TestCase):
    def setUp(self) -> None:
        View = FlowViewSet
        View.permission_classes = []

        self.factory = APIRequestFactory()
        self.url = "/internals/flows/"
        self.view = View.as_view(dict(post="create"))
        self.user = User.objects.create(email="fake@test.com")
        self.org = Org.objects.create(
            name=f"Org test",
            timezone="America/Maceio",
            created_by=self.user,
            modified_by=self.user,
        )

    @patch("temba.orgs.models.Org.import_app")
    def test_x_is_x(self, mock):
        data = dict(org=str(self.org.uuid), sample_flow="{}")
        request = self.factory.post(self.url, data=data)

        force_authenticate(request, user=self.user)
        response = self.view(request, org=str(self.org.uuid))

        print(response.data)
