import pytest

from django.test import TestCase
from django.test.utils import isolate_apps
from django.urls import reverse
from django.utils.translation import ugettext as _

from apps.core.factories import PIXELER_PASSWORD, PixelerFactory
from apps.core.tests.mixins.models import ModelWithStandardID, ModelWithUUID


@isolate_apps('apps.core.tests.mixins')
class UUIDModelMixinTestCase(TestCase):

    def test_get_short_uuid(self):

        m = ModelWithUUID.objects.create()
        expected = m.id.hex[:7]

        self.assertEqual(m.get_short_uuid(), expected)

    def test_get_short_uuid_without_uuid_model(self):

        m = ModelWithStandardID.objects.create()

        with self.assertRaises(TypeError) as e:
            m.get_short_uuid()

        self.assertEqual(
            str(e.exception),
            'ModelWithStandardID model id is not a valid UUID'
        )

    def test_model_representation(self):

        m = ModelWithUUID.objects.create()
        expected = m.id.hex[:7]

        self.assertEqual(str(m), expected)


class LoginRequiredTestMixin(object):
    """
    A mixin to test views with the login_required decorator.

    Nota bene: you must at least define an url property
    """

    method = 'get'
    template = None
    url = None

    def setUp(self):
        """Create simple user (not staff nor superuser)"""
        self.simple_user = PixelerFactory(
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

    def login(self):
        """User login shortcut"""
        return self.client.login(
            username=self.simple_user.username,
            password=PIXELER_PASSWORD,
        )

    def test_login_required(self):

        if self.url is None:
            raise NotImplementedError(
                _(
                    "You should define an url when your TestCase inherits from"
                    " the LoginRequiredTestCase"
                )
            )

        # User is not logged in, she should be redirected to the login form
        response = self.client.get(self.url)
        expected_url = '{}?next={}'.format(reverse('login'), self.url)
        self.assertRedirects(response, expected_url)

        # Log an active user in and then test we are not redirected
        self.assertTrue(self.login())

        response = eval('self.client.{}(self.url)'.format(self.method))
        self.assertEqual(response.status_code, 200)

        if self.template is not None:
            self.assertTemplateUsed(response, self.template)


class LoginRequiredMixinTestCase(TestCase):

    def test_declaring_url_attribute_is_mandatory(self):

        class FooViewTestCase(LoginRequiredTestMixin):
            pass

        foo = FooViewTestCase()

        with pytest.raises(NotImplementedError):
            foo.test_login_required()
