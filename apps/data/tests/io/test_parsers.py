from pathlib import Path

import pytest

from django.test import TestCase

from ...factories import EntryFactory, RepositoryFactory
from ...models import Entry
from ...io.parsers import CGDParser


class CGDParserTestCase(TestCase):

    def setUp(self):

        self.file_path = Path(
            'apps/data/fixtures/'
        ) / Path(
            'C_glabrata_CBS138_current_chromosomal_feature_10.tab'
        )

    def test_init(self):

        with pytest.raises(TypeError):
            CGDParser()

        parser = CGDParser(self.file_path)
        assert parser.file_path == self.file_path
        assert parser.features is None
        assert parser.entries == {'new': [], 'update': []}

    def test_parse(self):

        parser = CGDParser(self.file_path)
        assert parser.features is None

        parser.parse()
        assert len(parser.features) == 10

        first_feature = parser.features.iloc[0]
        assert first_feature['name'] == 'CAGL0A00105g'
        assert first_feature['description'] == 'Protein of unknown function'
        assert first_feature['id'] == 'CAL0000210339'

        last_feature = parser.features.iloc[-1]
        assert last_feature['name'] == 'CAGL0A02321g'
        assert last_feature['description'] == (
            'Ortholog(s) have fructose transmembrane transporter activity, '
            'glucose transmembrane transporter activity, mannose '
            'transmembrane transporter activity and role in fructose import '
            'across plasma membrane, glucose import across plasma membrane'
        )
        assert last_feature['id'] == 'CAL0126815'

    def test__to_entries(self):

        defaults = {'new': [], 'update': []}
        parser = CGDParser(self.file_path)
        assert parser.entries == defaults

        parser._to_entries(ignore_aliases=True)
        assert parser.entries == defaults

        parser.parse()
        parser._to_entries(ignore_aliases=True)
        assert parser.entries != defaults
        assert len(parser.entries['new']) == 10
        assert len(parser.entries['update']) == 0

        # Look for duplicates
        identifiers = [e.identifier for e in parser.entries['new']]
        assert len(identifiers) == len(set(identifiers))
        assert 'CAGL0A00105g' in identifiers
        assert 'CAGL0A02321g' in identifiers

        # Check two entries
        entry = parser.entries['new'][identifiers.index('CAGL0A00105g')]
        assert entry.identifier == 'CAGL0A00105g'
        assert entry.description == 'Protein of unknown function'
        assert entry.url == (
            'http://www.candidagenome.org/cgi-bin/locus.pl?dbid=CAL0000210339'
        )
        assert entry.repository.name == 'CGD'

        entry = parser.entries['new'][identifiers.index('CAGL0A02321g')]
        assert entry.identifier == 'CAGL0A02321g'
        assert entry.description == (
            'Ortholog(s) have fructose transmembrane transporter activity, '
            'glucose transmembrane transporter activity, mannose '
            'transmembrane transporter activity and role in fructose import '
            'across plasma membrane, glucose import across plasma membrane'
        )
        assert entry.url == (
            'http://www.candidagenome.org/cgi-bin/locus.pl?dbid=CAL0126815'
        )
        assert entry.repository.name == 'CGD'

    def test__to_entries_with_existing_entries(self):

        repository = RepositoryFactory(name='CGD')
        first_entry = EntryFactory(
            identifier='CAGL0A00105g',
            description='Old description',
            url=(
                'http://www.candidagenome.org/cgi-bin/locus.pl?dbid='
                'CAL0000210339'
            ),
            repository=repository
        )

        parser = CGDParser(self.file_path)
        parser.parse()
        parser._to_entries(ignore_aliases=True)

        assert len(parser.entries['new']) == 9
        assert len(parser.entries['update']) == 1
        assert parser.entries['update'][0].identifier == 'CAGL0A00105g'
        assert parser.entries['update'][0].description == (
            'Protein of unknown function'
        )
        assert parser.entries['update'][0].url == first_entry.url

    def test__to_entries_with_aliases(self):

        parser = CGDParser(self.file_path)
        parser.parse()
        parser._to_entries(ignore_aliases=False)

        assert len(parser.entries['new']) == 30
        assert len(parser.entries['update']) == 0

    def test_save(self):

        parser = CGDParser(self.file_path)
        parser.parse()

        assert Entry.objects.count() == 0

        parser.save()
        assert Entry.objects.count() == 10

        entry = Entry.objects.get(identifier='CAGL0A00105g')
        assert entry.url == (
            'http://www.candidagenome.org/cgi-bin/locus.pl?dbid=CAL0000210339'
        )

    def test_save_with_existing_entries(self):

        repository = RepositoryFactory(name='CGD')
        first_entry = EntryFactory(
            identifier='CAGL0A00759s',
            description='Old description',
            url=(
                'http://www.candidagenome.org/cgi-bin/locus.pl?dbid='
                'CAL0137785'
            ),
            repository=repository
        )
        assert Entry.objects.count() == 1

        parser = CGDParser(self.file_path)
        parser.parse()
        parser.save()
        assert Entry.objects.count() == 10

        entry = Entry.objects.get(url=first_entry.url)
        assert entry.id == first_entry.id
        # identifier/description should have been updated
        assert entry.identifier == first_entry.identifier
        assert entry.description == 'Centromere, chromosome A'

    def test_save_with_aliases(self):

        parser = CGDParser(self.file_path)
        parser.parse()

        assert Entry.objects.count() == 0

        parser.save(ignore_aliases=False)
        assert Entry.objects.count() == 30

        entry = Entry.objects.get(identifier='CAG57670.1')
        assert entry.url == (
            'http://www.candidagenome.org/cgi-bin/locus.pl?dbid=CAL0126541'
        )
