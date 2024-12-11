from django.views.generic.detail import SingleObjectMixin

from main.views.media.base_image_serve_view import BaseImageServeView


class SimpleImageServeView(SingleObjectMixin, BaseImageServeView):
    model = None  # Нужно передать правильный класс при создании view

    def get_image(self):
        return self.get_object().image
