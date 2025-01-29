DataDrivers отвечают за обработку данных
    Используют DbСontrollers чтобы взаимодействовать с базой данных
    IikoApi для взаимодействия с iiko


# TODO: Разделить логгер iiko и логгер проекта


UiControllers используют Datadrivers и отвечают за управление ui элементами




Добавить индикатор с пингом iiko отображающий онлайн/офлайн


Пройти по всем принтам и логам, принты заменить на логирование и где необходимо выбрасывать окно с ошибкой
Окно с ошибкой лучше выбрасывать на вернем уровне логики, а на нижней проталкивать райзы выше для перехвата
Для понимания происходящего можно внизу добавить строку где отображать информативные сообщения из логов

Написать небольшой модуль для инициализации который получит отделы и сохранит их в бд
так как iiko рекомендует их не запрашивать каждый раз а хранить на своей стороне
Можно создать для него окно в котором запросить данные для входа и необходимые стартовые конфиги


Добавить для работников признак "скрытый"
Для того чтобы можно было спрятать их из интерфейса 
и опцию отображать скрытые

Добавить таблицу для хранения информации последней синхронизации данных,
для вывода в UI "Данные актуальны на datetime"

Добавить отображение спорных явок


Своя модель данных для программ мотивации, при создании или редактировании открывается окно,
в котором три списка слева один по другим: все роли, 



Добавить строку состояния- понять как работает
Подумать над бэкапом

Допилить инициализацию iiko_API клиента, таким образом чтобы гибко подключать эндпоинты простым их добавлением в список,
список эндпоинтов можно хранить в файле config или config_endpoints, с остальными необходимыми для апи конфигами:


```python
from dataclasses import dataclass
from typing import Dict, List, Union, Optional

@dataclass
class BaseClient:
    session: str = "Authorized Session"

class EndpointA:
    def __init__(self, client: BaseClient):
        self.client = client
    
    def do_something(self):
        print(f"Do something with {self.client.session}")

class EndpointB:
    def __init__(self, client: BaseClient):
        self.client = client
    
    def do_another_thing(self):
        print(f"Do another thing with {self.client.session}")

class HighLevelClient:
    def __init__(self, endpoints: List[type]):
        self.client = BaseClient()
        self.endpoints = {}
        
        for endpoint_cls in endpoints:
            endpoint_name = endpoint_cls.__name__
            self.endpoints[endpoint_name] = endpoint_cls(self.client)
    
    def __getattr__(self, item):
        try:
            return self.endpoints[item]
        except KeyError as e:
            raise AttributeError(f"{item} is not a valid endpoint") from e

if __name__ == "__main__":
    high_level_client = HighLevelClient([EndpointA, EndpointB])
    
    high_level_client.EndpointA.do_something()  # Do something with Authorized Session
    high_level_client.EndpointB.do_another_thing()  # Do another thing with Authorized Session

```




БАГ: СОЗДАЛ ПРОГРАММУ МОТИВАЦИИ -> СОЗДАЛ ПОРОГ С СУММОЙ -> ЗАЩЕЛ В ДОБАВИТЬ СОТРУДНИКА ПЕРЕТЯНУЛ В ДОБАВИТЬ ->
ПЕРТЯНУЛ ОБРАТНО -> НЕПОМНЮ СОХРАНИЛ ИЛИ ОТМЕНИЛ -> УДАЛИЛ ПОРОГ -> УДАЛИЛ ПРОГРАММУ -> ВОЗНИКЛА ОШИБКА