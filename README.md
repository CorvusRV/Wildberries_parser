# Парсер для Wildberries

### Реализованно
1.	Скрипт позволяет получить информацию о товарах, продаваемых на площадке Wildberries: name, id, sale price, price, brand, brand id, supplier id, feedbacks, rating, product url, supplier url. Вся полученная информация сохраняется в CSV файл. Название файла складывается из запроса пользователя и текущей даты

### Технологии
* Python 3.10
* asyncio
* aiohttp
* csv

### Примечание:
В данной реализации может получить информацию максимум 6000 самых популярных товаров из запроса пользователя.
В начале работы скрипта необходимо ввести название товаров или группы товаров.
