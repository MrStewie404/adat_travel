import abc

from django.core.exceptions import ValidationError
from django.db import models

from main.models.abc_model import ABCModel
from main.models.agency.agency import Agency
from main.models.utils import file_upload_path
from main.utils.utils import is_valid_image, get_valid_filename_light


class AbstractMedia(ABCModel):
    """Абстрактная модель: медиафайл."""
    file = models.FileField('Файл', upload_to=file_upload_path)
    original_file_name = models.CharField('Исходное имя файла', max_length=256, editable=False)
    description = models.CharField('Описание', max_length=256, blank=True)

    @property
    @abc.abstractmethod
    def agency(self) -> Agency:
        """Абстрактное поле."""
        pass

    def is_valid_image(self):
        return is_valid_image(self.file.path, check_extension=True, max_width=13840, max_height=12160)

    def clean(self):
        if not self.file._committed:
            self.validate_file_size(self.file.file)
        super().clean()

    def save(self, *args, **kwargs):
        if not self.file._committed:
            self.original_file_name = get_valid_filename_light(self.file.name)  # Запоминаем исходное имя файла
        self.full_clean()
        return super().save(*args, **kwargs)

    @staticmethod
    def validate_file_size(file, max_size_mb=50):
        # TODO: написать тесты
        max_size_bytes = max_size_mb * 1024 * 1024
        if file:
            size = file.size
            if size > max_size_bytes:
                # Если файл слишком большой, выдаём ошибку. Но т.к. этот метод вызывается из метода clean
                # модели или формы, то к этому моменту весь файл уже загружен на сервер в папку tmp,
                # поэтому стоит также ограничить размер файлов в настройках сервера,
                # см. https://docs.djangoproject.com/en/4.0/topics/security/#user-uploaded-content-security
                raise ValidationError(f"Размер файла не должен превышать {max_size_mb} Мб", code='file_size_check_fail')
            if size == 0:
                raise ValidationError("Файл не может быть пустым", code='file_empty')

    class Meta:
        abstract = True
