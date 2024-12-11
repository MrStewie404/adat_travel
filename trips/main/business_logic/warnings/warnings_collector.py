from collections import OrderedDict

from django.db import models


class SeverityEnum(models.IntegerChoices):
    INFO = 0, 'Информация'
    WARNING = 1, 'Предупреждение'
    ERROR = 2, 'Ошибка'


class KeyInfo:
    def __init__(self, value, label):
        self.value = value
        self.label = label

    def __str__(self):
        return f"{self.value}:{self.label}"


class WarningsCollector:
    def __init__(self):
        self._messages = []
        self._collectors_by_key = OrderedDict()
        self._key_info_by_key = OrderedDict()
        self._tags = set()  # Для прикрепления дополнительной информации в виде тегов

    def extract_key(self, obj):
        if isinstance(obj, KeyInfo):
            return obj.value
        return str(obj)

    def __getitem__(self, key):
        return self._collectors_by_key[self.extract_key(key)]

    def get_or_default(self, key, default):
        try:
            return self[key]
        except KeyError:
            return default

    def get_joined_keys(self, *keys):
        collector = WarningsCollector()
        for key in keys:
            extended_key = self._key_info_by_key.get(key, key)
            collector[extended_key] = self.get_or_default(key, WarningsCollector())
        return collector

    def __setitem__(self, key, collector):
        correct_key = self.extract_key(key)
        if collector:
            self._collectors_by_key[correct_key] = collector
            if isinstance(key, KeyInfo):
                self._key_info_by_key[correct_key] = key
        else:
            self._collectors_by_key.pop(correct_key, None)
            self._key_info_by_key.pop(correct_key, None)

    def __bool__(self):
        """В конструкции вида "if collector" пустой collector будет себя вести так же, как и пустой список."""
        return not self.empty()

    def __str__(self):
        return self.get_string()

    def get_string(self, depth=1):
        if self.empty():
            return ''
        if depth <= 0:
            return self.get_messages_count_str(self.info_count(), self.warnings_count(), self.errors_count())
        messages = self.get_own_messages()
        for key, collector in self._collectors_by_key.items():
            label = key
            key_info = self._key_info_by_key.get(key, None)
            if key_info:
                label = key_info.label
            messages.append(self.get_sub_collector_str(collector, label=label, depth=depth))
        return '\n'.join(messages)

    def empty(self):
        return len(self._messages) == 0 and len(self._collectors_by_key) == 0

    def contains_warnings_or_errors(self):
        return self.warnings_and_errors_count() > 0

    def get_own_warnings(self):
        return self.get_own_messages(SeverityEnum.WARNING)

    def get_own_errors(self):
        return self.get_own_messages(SeverityEnum.ERROR)

    def get_own_messages(self, *severity_list):
        return [msg for (msg, msg_severity) in self._messages if not severity_list or msg_severity in severity_list]

    def info_count(self):
        return self.messages_count(SeverityEnum.INFO)

    def warnings_count(self):
        return self.messages_count(SeverityEnum.WARNING)

    def errors_count(self):
        return self.messages_count(SeverityEnum.ERROR)

    def warnings_and_errors_count(self):
        return self.warnings_count() + self.errors_count()

    def messages_count(self, *severity_list):
        count = len(self.get_own_messages(*severity_list))
        for collector in self._collectors_by_key.values():
            count += collector.messages_count(*severity_list)
        return count

    @property
    def tags(self):
        return self._tags

    def collect_warnings_custom(self, collect_warnings_fun):
        collect_warnings_fun(self)
        return self

    def add_message(self, msg, severity):
        self._messages.append((msg, severity))

    def add_warning(self, msg):
        self.add_message(msg, SeverityEnum.WARNING)

    def add_error(self, msg):
        self.add_message(msg, SeverityEnum.ERROR)

    def add_info(self, msg):
        self.add_message(msg, SeverityEnum.INFO)

    @staticmethod
    def get_messages_count_str(info_count, warnings_count, errors_count):
        from main.templatetags.pluralize_ru import pluralize_ru
        errors_str = f"{errors_count} ошиб{pluralize_ru(errors_count, 'ка,ки,ок')}" \
            if errors_count > 0 else ""
        warnings_str = f"{warnings_count} предупрежден{pluralize_ru(warnings_count, 'ие,ия,ий')}" \
            if warnings_count > 0 else ""
        info_str = f"{info_count} сообщен{pluralize_ru(info_count, 'ие,ия,ий')}" \
            if info_count > 0 else ""
        parts = [x for x in (errors_str, warnings_str, info_str) if x]
        return ', '.join(parts)

    @staticmethod
    def get_sub_collector_str(collector, label, depth):
        if depth == 1 and collector.messages_count() == 1:
            collector_str = collector.get_string(depth=1)
            return f"{label} · {collector_str}" if label else collector_str
        label_and_msg_sep = '\n' if depth > 1 else ' '
        collector_str = collector.get_string(depth=depth - 1)
        return f"{label} · {label_and_msg_sep}{collector_str}" if label else collector_str

    @staticmethod
    def with_warnings(*args):
        collector = WarningsCollector()
        for msg in args:
            collector.add_warning(msg)
        return collector
