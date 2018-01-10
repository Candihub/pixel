from django.dispatch import Signal


importation_done = Signal(
    providing_args=['experiment', 'analysis', 'pixel_sets']
)
