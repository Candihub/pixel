from .. import factories, models
from . import CoreFixturesTestCase


class AnalysisFactoryTestCase(CoreFixturesTestCase):

    def test_new_factory_with_Experiments(self):

        experiments = factories.ExperimentFactory.create_batch(3)

        # build
        analysis = factories.AnalysisFactory.build(experiments=experiments)
        self.assertEqual(analysis.experiments.count(), 0)

        # create
        analysis = factories.AnalysisFactory(experiments=experiments)

        experiments_ids = analysis.experiments.values_list(
            'id', flat=True
        )
        expected_experiments_ids = models.Experiment.objects.values_list(
            'id', flat=True
        )
        self.assertEqual(
            list(experiments_ids),
            list(expected_experiments_ids)
        )
