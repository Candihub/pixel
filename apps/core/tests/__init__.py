from django.test import TestCase


class CoreFixturesTestCase(TestCase):

    fixtures = [
        'apps/data/fixtures/initial_data.json',
        'apps/core/fixtures/initial_data.json',
    ]
