# Взято отсюда https://stackoverflow.com/questions/4695609/checking-date-against-date-range-in-python/48957701#48957701?newreg=d472fcbe94ce4e6c9f79025059b78702
# Класс для проверки того, что дата в диапазоне
# test_true in DatetimeRange(dt1, dt2) #Returns True
# test_false in DatetimeRange(dt1, dt2) #Returns False
class DatetimeRange:
    def __init__(self, dt1, dt2):
        self._dt1 = dt1
        self._dt2 = dt2

    def __contains__(self, dt):
        return self._dt1 < dt < self._dt2
