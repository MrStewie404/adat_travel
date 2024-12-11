import datetime


class SeasonDate(datetime.date):
    """
    Специальный вид даты для сезонных событий/сущностей
    (год всегда заменяется на datetime.MINYEAR, используются только месяц и день).
    """

    def __new__(cls, month=None, day=None):
        if month == 2 and day == 29:
            day = 28
        inst = super().__new__(cls, datetime.MINYEAR, month, day)
        return inst

    @classmethod
    def from_date(cls, date):
        return cls(date.month, date.day)
