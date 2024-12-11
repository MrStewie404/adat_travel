import re
from datetime import date

from django.core.exceptions import ValidationError
from django.forms import ModelForm

from main.forms.common.widgets import text_input, select, textarea, date_input


class BasePersonForm(ModelForm):
    def clean_surname(self):
        surname = self.cleaned_data.get('surname').strip()
        if surname:
            self.check_characters_in_any_name(surname)
        return surname

    def clean_name(self):
        name = self.cleaned_data.get('name').strip()
        if len(name) < 2:
            raise ValidationError("Введено слишком короткое имя", code='name_length_fail')
        self.check_characters_in_any_name(name)
        return name

    def clean_middle_name(self):
        middle_name = self.cleaned_data.get('middle_name').strip()
        if middle_name:
            self.check_characters_in_any_name(middle_name)
        return middle_name

    def clean_date_birth(self):
        date_birth = self.cleaned_data.get('date_birth')
        if date_birth and date_birth > date.today():
            raise ValidationError("Некорректная дата рождения", code='date_birth_check_fail')
        return date_birth

    @staticmethod
    def check_characters_in_any_name(text):
        if not re.match(r"^[a-zA-Zа-яёА-ЯЁ\-.' ]*$", text):
            raise ValidationError("Допустимы буквы русского или латинского алфавитов, "
                                  "а также специальные символы (пробел, точка, дефис, апостроф).",
                                  code='full_name_check_fail')

    class Meta:
        fields = ['surname', 'name', 'middle_name', 'sex', 'date_birth', 'place_birth',
                  'food_preferences', 'comment']
        widgets = {
            'surname': text_input(''),
            'name': text_input(''),
            'middle_name': text_input(''),
            'sex': select(),
            'date_birth': date_input('', height=35),
            'place_birth': text_input(''),
            'food_preferences': textarea(''),
            'comment': textarea('', rows=3),
        }
