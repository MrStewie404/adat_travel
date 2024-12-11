import abc

from main.business_logic.warnings.warnings_collector import WarningsCollector


class ModelWarningsProvider(abc.ABC):
    def __init__(self, model):
        self.model = model

    def is_enabled(self):
        return True

    def create_collector(self):
        return WarningsCollector()

    def get_warnings(self):
        if not self.is_enabled():
            return None
        return self.create_collector().collect_warnings_custom(self.collect_warnings)

    def collect_warnings_if_enabled(self, warnings_collector):
        if not self.is_enabled():
            return
        self.collect_warnings(warnings_collector)

    @abc.abstractmethod
    def collect_warnings(self, warnings_collector):
        pass
