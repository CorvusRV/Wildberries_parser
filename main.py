import asyncio
import aiohttp
import csv
from datetime import date


class ParserWB:
    def __init__(self, query):
        self.headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        self.url = 'https://search.wb.ru/exactmatch/ru/common/v4/'
        self.query = query
        self.counts_of_sessions = 0
        self.product_list = []

    async def analysis_of_the_number_of_goods(self, session):
        """определение кол-ва сессиий"""
        url_count = f'{self.url}search?appType=1&curr=rub&dest=-1257786&query={self.query}' \
                    f'&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,31,22,71,114' \
                    f'&resultset=filters&spp=0&suppressSpellcheck=false'
        async with session.get(url=url_count, headers=self.headers) as response:
            response_json = await response.json(content_type=None)
        count_goods: int
        count_goods = response_json['data']['total']

        if count_goods < 6000:
            print(f"Всего найдено {count_goods} товаров, будут загружены данные о всех товарах")
            self.counts_of_sessions = count_goods // 100 + (0 if count_goods % 100 == 0 else 1)
        else:
            print(f"Всего найдено {count_goods} товаров. Будут получены данные о 6000 самых популярных товаров")
            self.counts_of_sessions = 60

    async def data_extraction(self, json):
        """извлечение данных из json"""
        if json.get('data') is None or json.get('data').get('products') is None:
            return
        for product in json['data']['products']:
            self.product_list.append({
                'Наименование': product['name'],
                'id': product['id'],
                'Цена': int(product['salePriceU']) / 100,
                'Цена до скидки': int(product['priceU']) / 100,
                'Скидка': product['sale'],
                'Бренд': product['brand'],
                'id бренда': product['brandId'],
                'id продавца': product['supplierId'],
                'feedbacks': product['feedbacks'],
                'rating': product['rating'],
                'ссылка на товар': f'https://www.wildberries.ru/catalog/{product["id"]}/detail.aspx',
                'ссылка на продавца': f'https://www.wildberries.ru/seller/{product["supplierId"]}'
            })

    async def get_product_data_from_json(self, session, page):
        """постраничное получение json с данными о товарах и извлечение данных из json"""
        url_page = f'{self.url}search?appType=1&curr=rub&dest=-1075831,-77677,-398551,12358499&page={page}' \
                   f'&query={self.query}&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,31,22,71,114' \
                   f'&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false'

        async with session.get(url=url_page, headers=self.headers) as response:
            json = await response.json(content_type=None)
            await self.data_extraction(json)

    def save_excel(self):
        """сохранение результата в csv файл"""
        columns = self.product_list[0].keys()
        with open(f'{self.query} {date.today()}.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile, dialect='excel', delimiter=';')
            writer.writerow(columns)
            for product in self.product_list:
                writer.writerow(product.values())

    async def session_creation(self):
        """создание сессии для асинхронного парсинга"""
        async with aiohttp.ClientSession() as session:
            await self.analysis_of_the_number_of_goods(session)
            await asyncio.sleep(1)
            tasks = []
            for page in range(1, self.counts_of_sessions + 1):
                task = asyncio.create_task(self.get_product_data_from_json(session, page))
                tasks.append(task)
            await asyncio.gather(*tasks)
            self.save_excel()

    def start_asynchronous_parsing(self):
        """начало работы парсера"""
        asyncio.run(self.session_creation())


if __name__ == '__main__':
    query = input('Введите поисковый запрос: ')
    print("Идет обработка...")
    ParserWB(query).start_asynchronous_parsing()
    print("Обработка завершена")