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
                ' JOIN core_omicsunit ON omics_unit_id = core_omicsunit.id'
                ' JOIN core_strain ON core_omicsunit.strain_id = core_strain.id'
                ' JOIN core_species ON core_strain.species_id = core_species.id'
                ' GROUP BY core_species.name'
            ))

            return render(request, 'core/home-authenticated.html', {
                'pixels_by_species': {
                    'title': _('Pixels by Species'),
                    'data': [[row.name, row.nb] for row in pixels_by_species],
                },
            })

        return super().get(request, *args, **kwargs)
