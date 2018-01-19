from .. import factories
from . import CoreFixturesTestCase


class AnalysisFactoryTestCase(CoreFixturesTestCase):

    def test_new_factory_with_Experiments(self):

        experiments = factories.ExperimentFactory.create_batch(3)

        # build
        analysis = factories.AnalysisFactory.build(experiments=experiments)
        self.assertEqual(analysis.experiments.count(), 0)

        # create
        analysis = factories.AnalysisFactory(experiments=experiments)

        experiments_ids = list(
            analysis.experiments.values_list('id', flat=True)
        )
        expected_experiments_ids = [e.id for e in experiments]
        self.assertEqual(experiments_ids, expected_experiments_ids)
