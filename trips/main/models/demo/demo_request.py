from django.db import models
from django.contrib import admin


class DemoRequest(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    company_name = models.CharField(max_length=100, blank=True, null=True,  verbose_name='Организация')
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    proceed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Запрос демо доступа'
        verbose_name_plural = 'Запросы демо доступа'


class DemoRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'company_name', 'created_at', 'proceed')
