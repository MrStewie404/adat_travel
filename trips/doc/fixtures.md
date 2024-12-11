# Fixtures в нашем проекте и как ими пользоваться

## Что это такое

Fixture - это файл в формате json, в котором хранятся данные из БД. 
Скрипт manage.py позволяет выгружать данные из БД в fixture, и наоборот, загружать данные из fixture в БД.
Fixtures подходят для хранения тестовых данных или для различных "патчей" 
для предзаполнения БД данными. Например, у нас в проекте есть fixtures 
для создания (обновления) предустановленных групп пользователей.

## Где лежит

В нашем проекте fixtures лежат в папке [main/fixtures](./trips/main/fixtures/):
* demo_data.json - данные, использованные для предзаполнения БД на основном сайте (он же "demo")
* services_adat.json - тестовые службы для АДАТ
* test_data.json - для заполнения БД тестовыми данными по клиентам и турам
* test_users_adat.json - тестовые пользователи для АДАТ
* user_groups.json - для добавления/обновления "предустанавливаемых" в систему групп пользователей 

## Как пользоваться

Заполнение чистой БД на локальной машине тестовыми данными, добавление пользователей:
```bash
python manage.py loaddata main/fixtures/test_data.json main/fixtures/services_adat.json main/fixtures/user_groups.json main/fixtures/test_users_adat.json
```

Обновление групп пользователей в БД (права всех "предустанавливаемых" групп будут полностью перезаписаны):
```bash
python manage.py loaddata main/fixtures/user_groups.json
```

Экспорт таблиц из БД в файл test_data.json, для создания тестовых fixtures:

```bash
python -Xutf8 manage.py dumpdata --natural-foreign --natural-primary --indent=2 --exclude=auth --exclude=contenttypes --exclude=sessions --exclude=admin --output=main/fixtures/test_data.json
```

---

Экспорт таблиц с пользователями и их правами:
```bash
python -Xutf8 manage.py dumpdata auth --natural-foreign --natural-primary --indent=2 -e auth.Permission --output=main/fixtures/auth.json
```
