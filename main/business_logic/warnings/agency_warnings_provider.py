from main.business_logic.warnings.model_warnings_provider import ModelWarningsProvider
from main.business_logic.warnings.warnings_collector import WarningsCollector, KeyInfo
from main.models.trips.tourists.trip_company import TripCompany


class AgencyWarningsProvider(ModelWarningsProvider):
    @property
    def agency(self):
        return self.model

    def collect_warnings(self, warnings_collector):
        warnings_collector[KeyInfo("draft_companies", "Новые заявки")] = \
            WarningsCollector().collect_warnings_custom(self.collect_draft_companies_warnings)

    def collect_draft_companies_warnings(self, warnings_collector):
        count = TripCompany.objects.filter(trip__agency=self.agency, is_draft=True).count()
        if count > 0:
            from main.templatetags.pluralize_ru import pluralize_ru
            warnings_collector.add_warning(
                f"{count} {pluralize_ru(count, 'новая заявка,новые заявки,новых заявок')}"
            )
