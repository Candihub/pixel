from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory


class RepositoryFactory(DjangoModelFactory):

    name = Faker('word')
    url = Faker('url')

    class Meta:
        model = 'data.Repository'
        django_get_or_create = ('name', )


class EntryFactory(DjangoModelFactory):

    identifier = Sequence(lambda n: 'FK-{:06d}'.format(n))
    description = Faker('text', max_nb_chars=300)
    url = Faker('url')
    repository = SubFactory(RepositoryFactory)

    class Meta:
        model = 'data.Entry'
        django_get_or_create = ('identifier', )
