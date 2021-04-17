from django.db.models.signals import post_save

from .models import Alternative
from .utils import reshape_img_to_square_with_blurry_bg


'''
def my_callback(sender, instance, created, **kwargs):
    bg_img = reshape_img_to_square_with_blurry_bg(instance.image.name)
    bg_img.save(instance.image.path)


post_save.connect(my_callback, sender=Alternative)
'''
