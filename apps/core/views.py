from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.shortcuts import render


from apps.core.models import Pixel
from apps.core.models import Pixeler


class HomeView(TemplateView):

    template_name = 'core/home.html'

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated():
            pixels_by_species = Pixel.objects.raw((
                'SELECT core_species.name AS name, count(*) AS nb,'
                ' 1 AS id'  # this is a hack to overcome Django ORM limitations
                ' FROM core_pixel'
                ' JOIN core_omicsunit'
                '   ON omics_unit_id = core_omicsunit.id'
                ' JOIN core_strain'
                '   ON core_omicsunit.strain_id = core_strain.id'
                ' JOIN core_species'
                '   ON core_strain.species_id = core_species.id'
                ' GROUP BY core_species.name'
            ))

            omics_area_tree = Pixel.objects.raw((
                "SELECT core_omicsarea_1.name AS area,"
                " COALESCE(core_omicsarea_2.name, 'Area') AS parent, "
                " 1 AS id"  # this is a hack to overcome Django ORM limitations
                " FROM core_omicsarea core_omicsarea_1"
                " LEFT JOIN core_omicsarea core_omicsarea_2"
                " ON core_omicsarea_1.parent_id = core_omicsarea_2.id;"
            ))

            pixels_by_omics_unit_type = Pixel.objects.raw((
                'SELECT core_omicsunittype.name AS name, count(*) AS nb,'
                ' 1 AS id'  # this is a hack to overcome Django ORM limitations
                ' FROM core_pixel'
                ' JOIN core_omicsunit'
                '   ON omics_unit_id = core_omicsunit.id'
                ' JOIN core_omicsunittype'
                '   ON core_omicsunit.type_id = core_omicsunittype.id'
                ' GROUP BY core_omicsunittype.name'
            ))

            pixels_by_omics_area = Pixel.objects.raw((
                'SELECT core_omicsarea.name AS name, count(*) AS nb,'
                ' 1 AS id'  # this is a hack to overcome Django ORM limitations
                ' FROM core_pixel'
                ' JOIN core_pixelset'
                '   ON pixel_set_id = core_pixelset.id'
                ' JOIN core_analysis'
                '   ON core_pixelset.analysis_id = core_analysis.id'
                ' JOIN core_analysis_experiments'
                '   ON core_analysis.id = '
                '   core_analysis_experiments.analysis_id'
                ' JOIN core_experiment'
                '   ON core_analysis_experiments. experiment_id = '
                '   core_experiment.id'
                ' JOIN core_omicsarea'
                '   ON core_experiment.omics_area_id = core_omicsarea.id'
                ' WHERE core_omicsarea.level = 0'
                ' GROUP BY core_omicsarea.name'
            ))

            number_of_pixelers = Pixeler.objects.count()

            return render(request, 'core/home-authenticated.html', {
                'pixels_by_species': {
                    'title': _('Pixels by Species'),
                    'data': [[row.name, row.nb] for row in pixels_by_species],
                },

                'omics_area_tree': {
                    'title': _('Omics area tree'),
                    'data': [[row.area, row.parent] for row
                             in omics_area_tree],
                },

                'pixels_by_omics_unit_type': {
                    'title': _('Pixels by Omics unit type'),
                    'data': [[row.name, row.nb] for row in
                             pixels_by_omics_unit_type],
                },

                'pixels_by_omics_area': {
                    'title': _('Pixels by Omics area'),
                    'data': [[row.name, row.nb] for row in
                             pixels_by_omics_area],
                },

                'number_of_pixelers': number_of_pixelers,

            })

        return super().get(request, *args, **kwargs)
