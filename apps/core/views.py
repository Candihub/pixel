from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.shortcuts import render


from apps.core.models import Pixel


class HomeView(TemplateView):

    template_name = 'core/home.html'

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated():
            pixels_by_species = Pixel.objects.raw((
                'SELECT core_species.name AS name, count(*) AS nb,'
                ' 1 as id'  # this is a hack to overcome Django ORM limitations
                ' FROM core_pixel'
                ' JOIN core_omicsunit'
                '   ON omics_unit_id = core_omicsunit.id'
                ' JOIN core_strain'
                '   ON core_omicsunit.strain_id = core_strain.id'
                ' JOIN core_species'
                '   ON core_strain.species_id = core_species.id'
                ' GROUP BY core_species.name'
            ))

            pixels_by_OmicsUnitType = Pixel.objects.raw((
                'SELECT core_OmicsUnitType.name AS name, count(*) AS nb,'
                ' 1 as id'  # this is a hack to overcome Django ORM limitations
                ' FROM core_pixel'
                ' JOIN core_omicsunit'
                '   ON omics_unit_id = core_omicsunit.id'
                ' JOIN core_OmicsUnitType'
                '   ON core_omicsunit.type_id = core_OmicsUnitType.id'
                ' GROUP BY core_OmicsUnitType.name'
            ))

            pixels_by_OmicsArea = Pixel.objects.raw((
                'SELECT core_OmicsArea.name AS name, count(*) AS nb,'
                ' 1 as id'  # this is a hack to overcome Django ORM limitations
                ' FROM core_pixel'
                ' JOIN core_PixelSet'
                '   ON pixel_set_id = core_PixelSet.id'
                ' JOIN core_Analysis'
                '   ON core_PixelSet.analysis_id = core_Analysis.id'
                ' JOIN core_analysis_experiments'
                '   ON core_Analysis.id = '
                '   core_analysis_experiments.analysis_id'
                ' JOIN core_Experiment'
                '   ON core_analysis_experiments. experiment_id = '
                '   core_Experiment.id'
                ' JOIN core_OmicsArea'
                '   ON core_Experiment.omics_area_id = core_OmicsArea.id'
                ' where core_OmicsArea.level = 0'
                ' GROUP BY core_OmicsArea.name'
            ))

            saved_analysis = Pixel.objects.raw((
                "Select to_char(saved_at, 'YYYY,MM,DD') AS date,"
                " count(*) AS nb,"
                " 1 as id"
                " FROM core_analysis"
                " GROUP BY date;"
            ))

            pixelers_infos = Pixel.objects.raw((
                "Select first_name, last_name, email,"
                " to_char(date_joined, 'YYYY-MM-DD') as date, 1 as id"
                " from core_pixeler"
                " order by last_name;"
            ))

            tags_infos = Pixel.objects.raw((
                "select slug, count,"
                " 1 as id"
                " from core_tag;"
            ))

            return render(request, 'core/home-authenticated.html', {
                'pixels_by_species': {
                    'title': _('Pixels by Species'),
                    'data': [[row.name, row.nb] for row in pixels_by_species],
                },

                'pixels_by_OmicsUnitType': {
                    'title': _('Pixels by Omics unit type'),
                    'data': [[row.name, row.nb] for row in
                             pixels_by_OmicsUnitType],
                },

                'pixels_by_OmicsArea': {
                            'title': _('Pixels by Omics area'),
                            'data': [[row.name, row.nb] for row in
                                     pixels_by_OmicsArea],
                },
                'saved_analysis': {
                            'title': _('Saved analysis'),
                            'data': [[row.date, row.nb] for row in
                                     saved_analysis],
                },

                'pixelers_infos': {
                            'title': _('Pixelers'),
                            'data': [[row.first_name, row.last_name,
                                      row.email, row.date] for row in
                                     pixelers_infos],
                },

                'tags_infos': {
                            'title': _('Tags'),
                            'data': [[row.slug, row.count] for row in
                                     tags_infos],
                },

            })

        return super().get(request, *args, **kwargs)
