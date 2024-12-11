from django.core.exceptions import ValidationError
from django.db import models

from main.models.agency.agency_employee import AgencyEmployee
from main.models.utils import file_upload_path, replace_image_with_thumbnail


class AgencyEmployeeAvatar(models.Model):
    """Профиль сотрудника турфирмы."""
    employee = models.OneToOneField(AgencyEmployee, on_delete=models.CASCADE, blank=True, null=True,
                                    related_name='avatar')
    image = models.ImageField('Аватар', upload_to=file_upload_path)

    max_width = 800
    max_height = 800

    def __str__(self):
        return f"Аватар сотрудника {self.employee.full_name()}"

    def clean(self):
        if not self.image._committed:
            if self.image.width > self.max_width or self.image.height > self.max_height:
                raise ValidationError(
                    f"Размер картинки не должен превышать {self.max_width}x{self.max_height}",
                    code='image_check_fail'
                )
            from main.models.abstract_media import AbstractMedia
            AbstractMedia.validate_file_size(self.image.file, max_size_mb=5)
            replace_image_with_thumbnail(self, 'image')
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Аватар сотрудника'
        verbose_name_plural = 'Аватары сотрудников'
