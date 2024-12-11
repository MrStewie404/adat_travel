from django.db import models


class AbstractIdentityDocument(models.Model):
    """Абстрактная модель: данные о документе, удостоверяющем личность."""

    class DocumentTypeEnum(models.TextChoices):
        PASSPORT_RU = 'PASSPORT_RU', 'Паспорт РФ'
        PASSPORT_ZAGRAN = 'PASSPORT_ZAGRAN', 'Заграничный паспорт'
        RESIDENCE_PERMIT = 'RESIDENCE_PERMIT', 'Вид на жительство иностранного гражданина'
        BIRTH_CERTIFICATE = 'BIRTH_CERTIFICATE', 'Свидетельство о рождении'

        __empty__ = '(Выберите вид документа)'

    document_type = models.CharField(
        'Вид документа',
        max_length=32,
        choices=DocumentTypeEnum.choices,
        blank=False
    )
    document_series = models.CharField('Серия', max_length=16, blank=True)
    document_number = models.CharField('Номер', max_length=32)
    issued_by = models.CharField('Выдан', max_length=256, blank=True)
    issue_date = models.DateField('Дата выдачи', blank=True, null=True)
    issue_office_code = models.CharField('Код подразделения', max_length=8, blank=True)

    def __str__(self):
        return f"{self.document_type_str()}: {self.document_series} {self.document_number}"

    def document_type_str(self):
        return self.get_document_type_display() if self.document_type else 'Неизвестный документ'

    class Meta:
        abstract = True
