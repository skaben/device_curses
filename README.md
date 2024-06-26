# smart_tester

основа для умного девайса.

https://github.com/skaben/device_boilerplate/releases/tag/1.0 - для этого стоит брать релиз

- [ ] все Boilerplate переименуйте в желаемое имя устройства.
- [ ] опишите логику работы внутри `device.py`
- [ ] опишите минимальный конфиг внутри `config.py`
- [ ] перед стартом необходимо сказать `./pre-run.sh install` для создания виртуального окружения и копирования системного конфига.
- [ ] после любой правки конфига в `templates/system_config.yml.template` необходим `./pre-run.sh reset` 
- [ ] не стоит забывать про виртуальное окружение, которое не активируется по умолчанию, `source ./venv/bin/activate`
- [ ] `python app.py` запустит приложение.

компоненты:

### device

содержит интерфейс с локальным конфигурационным файлом и отправки сообщений на сервер.

```
    state_reload -> загрузить текущий локальный конфиг из файла
    state_update(data -> dict) -> записать данные в локальный конфиг и послать на сервер
    send_message(data -> any) -> отправить сообщение без записи в локальный конфиг
```

### config

- системный конфиг генерируется из `templates/system_config.yml.template`, в процессе работы приложения не изменяется, хранится в `conf/system.yml`.
- конфиг устройства (приложения) изменяется в ходе работы, при первом запуске минимальный конфиг, описанный в `config.ESSENTIAL` будет записан в файл `conf/device.yml`

##### templates

При необходимости правим темплейт в `templates/system_config.yml.template`, либо вносим правки в уже существующий `conf/system.yml` - он перезаписывается только при запуске `pre-run.sh`
###### Параметры конфигурации:

`topic: <name>` \
определяет каналы MQTT. Для топика **lock** итоговый набор примет значения:

**pub:** /ask/lock/<MAC-address> \
**sub:** /lock/all/#, /lock/<MAC-address>/# \

`broker_ip: <broker ip address>`\
адрес MQTT-брокера

`username: <username>` \
имя пользователя для MQTT

`password: <password>` \
пароль для MQTT

`iface: ${iface}` \
определит внешний интерфейс автоматически в процессе работы ./pre-run.sh

`debug: bool` \
значение true включает дебаг

`standalone: bool` \
значение true выключает MQTT модуль

`external_logging: <20|30|40>`  
будет отправлять логи на сервер в виде INFO пакетов с минимальным уровнем:\
20 - INFO, \
30 - WARN, \
40 - ERROR, \
значение 10 (DEBUG) **использовать не стоит** чтобы не создавать нагрузку на сеть. Но вы, конечно, можете это сделать.

Если эти изменения вносились в `templates/system_config.yml.template` - запускаем `./pre-run.sh reset`

##### config.py

В классе конфигурации устройства могут быть расширены правила обработки входящей конфигурации.
Класс DeviceConfig предлагает базовый функционал устройства.
Наследование класса от DeviceConfigExtended включает поддержку API загрузки файлов и сторонних JSON из url

```
ESSENTIAL = {
    "key": 'val'
}
```

##### device.py

Создаем класс с желаемым именем, не забываем поправить имя класса конфига.

```
class CloseDevice(BaseDevice)

    config_class = CloseConfig

    def __init__(self, system_config, device_config, **kwargs):
        super().__init__(system_config, device_config)
        self.running = None
```
описываем поведение устройства
```
    def run(self):
        super().run()
        self.running = True
        while self.running:
            status = self.check_status()
```
сохраняем состояние
```
            if status == "closed":
                self.state_update({"closed": True})
```
или отправляем любое сообщение о событии
```
            elif status == "touched":
                self.send_message("I was touched")
```
