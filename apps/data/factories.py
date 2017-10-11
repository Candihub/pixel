from factory import Faker
from factory.django import DjangoModelFactory


class RepositoryFactory(DjangoModelFactory):

    name = Faker('word')
    url = Faker('url')

    class Meta:
        model = 'data.Repository'
        django_get_or_create = ('name', )
