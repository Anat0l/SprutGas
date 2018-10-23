import core
import MOD

# работа напрямую с газоанализаторами
DIRECT_MODE = "0"
# работа с БУПС
BUPS_MODE = "1"
# приём SMS и передача на пульт
SMS_RECIEVE_MODE = "2"

# Режим отправки на телефонные номера
SEND_MODE_PHONE = "0"
# Режим отправки на модем системы дубль
SEND_MODE_MODEM = "1"

# Ключи в настройках
# Скорость на серийном порту
SER_SP = "SER_SP"
# Скорость на серийном порту для отладки
DEBUG_SER_SP = "DEBUG_SER_SP"
# Режим работы последовательного порта для отладки
DEBUG_SER_OD = "DEBUG_SER_OD"
# Тип байта на серийном порту
SER_OD = "SER_OD"
# Выводить отладку
DEBUG_SER = "DEBUG_SER"
# Режим отправки SMS
SEND_MODE = "SEND_MODE"
# Режим работы
WORK_MODE = "WORK_MODE"
# Адреса газанализаторов
GAS_ADDRESS = "GAS_ADDRESS"

# Максимальный адрес устройства
MAX_ADDRESS = 255
# Таймаут чтения
READ_TIMEOUT = 1
# Таймаут ожидания запуска после рестарта
REBOOT_WAIT_TIMEOUT = 100

# Задержка в работе
WORK_DELAY = 1

# Текст сообщений
NO_CONNECTION_TEXT = "Нет связи с системой СГК"
CONNECTED_TEXT = "Связь с системой СГК установлена"

# Описание тревоги
class Alarm:
    # Конструктор
    # code - код тревоги
    # state - состояние: вкл/откл
    # txt - текстовое описание
    def __init__(self, code, state, text):
        self.code = code
        self.state = state
        self.text = text

# Для получения списка абонентов кому рассылать
class RecepientHelper:
    # Конструктор
    def __init__(self, config, gsm, debug):
        self.config = config
        self.gsm = gsm
        self.debug = debug

    # Возвращает список кому отправить SMS в зависимости от настроек
    def getRecepients(self):        
        sendMode = self.config.get(SEND_MODE)
        a, s = self.gsm.sendATMdmDefault("AT&N\r", "OK")
        phoneItems = s.split("\n")

        phones = []
        for item in phoneItems:
            its = item.split(";")            
            if (len(its) == 2):
                val = its[1].strip()
                if len(val) > 0:
                    phones.append(val)

        if sendMode == SEND_MODE_PHONE:
            return phones
        elif sendMode == SEND_MODE_MODEM:
            return [phones[0]]

# Хранилище тревог
# Если есть изменение тревоги сигнализирует об этом
class AlarmStorage:
    # Конструктор
    def __init__(self):
        self.alarms = {}

    # Добавляет тревогу
    # Если было изменение, возвращает тревогу
    def add(self, alarm):
        if self.alarms.has_key(alarm.code):
            info = self.alarms[alarm.code]
            if info.state != alarm.state:
                info.state = alarm.state
                info.text = alarm.text
                return info
            else:
                return None
        else:
            self.alarms[alarm.code] = alarm
            return info

# Парсер тревог полученных от устройства
class AlarmParser:
    def __init__(self):
        pass

    # Парсит тревоги газ анализаторов и первый байт бупса
    def parseOne(self):
        alarms = []
        if (code & 0x40 > 0) and (code & 1 > 0):
            alarms.append(Alarm(1, "Второй порог СН4"))
        if (code & 0x40 == 0) and (code & 0x01 > 0):
            alarms.append(Alarm(2, "Второй порог СО"))
        if (code & 0x04 > 0):
            alarms.append(Alarm(3, "Неисправность"))
        if (code & 0x01 == 0) and (code & 0x02 > 0) and (code & 0x04 == 0) and (code & 0x40 == 0):
            alarms.append(Alarm(4, "Первый порог СН4"))
        if (code & 0x01 == 0) and (code & 0x04 == 0) and (code & 0x08 > 0) and (code & 0x40 == 0):
            alarms.append(Alarm(5, "Первый порог СО"))
        if (code & 0x01 == 0) and (code & 0x04 == 0) and (code & 0x08 > 0) and (code & 0x40 > 1):
            alarms.append(Alarm(6, "Первый порог СН4"))
        if (code & 0x01 == 0) and (code & 0x02 > 0) and (code & 0x04 == 0) and (code & 0x40 > 1):
            alarms.append(Alarm(7, "Первый порог СО"))
        if (code & 0x10 == 0):
            alarms.append(Alarm(8, "Клапан открыт"))
        if (code & 0x10 > 0):
            alarms.append(Alarm(9, "Клапан закрыт"))
        
        return alarms

    # Парсит тревоги из второго байта бупс
    def parseTwo(self):
        alarms = []
        if (code & 0x81 > 0):
            alarms.append(Alarm(20, "Постановка на охрану"))
        if (code & 0x82 > 0):
            alarms.append(Alarm(21, "Взлом"))
        if (code & 0x84 > 0):
            alarms.append(Alarm(22, "Пожар"))
        if (code & 0x88 > 0):
            alarms.append(Alarm(23, "Авария 1"))
        if (code & 0x90 > 0):
            alarms.append(Alarm(24, "Авария 2"))
        
        return alarms

    # Парсит тревоги из третьего байта бупс
    def parseThree(self):
        # Не нужен пока что
        pass

    # Парсит тревоги из четвёртого байта бупс
    def parseFour(self):
        alarms = []
        if (code & 0xC1 > 0):
            alarms.append(Alarm(40, "Авария 8"))
        if (code & 0xC2 > 0):
            alarms.append(Alarm(41, "Авария 9"))
        if (code & 0xC4 > 0):
            alarms.append(Alarm(42, "Авария 10"))
        if (code & 0xC8 > 0):
            alarms.append(Alarm(43, "Авария 11"))
        if (code & 0xD0 > 0):
            alarms.append(Alarm(44, "Авария 12"))
        
        return alarms

# Обеспечивает работу в режиме опроса газовых анализаторов
class DirectWorker:
    # Конструктор
    def __init__(self, config):
        self.config = config

        self.speed = config.get(SER_SP)
        self.serial = core.Serial()

        isDebug = config.get(DEBUG_SER) == "1"
        debugSpeed = config.get(DEBUG_SER_SP)
        debugBytetype = config.get(DEBUG_SER_OD)
        self.debug = core.Debug(isDebug, self.serial,
                                debugSpeed, debugBytetype)
        
        self.gsm = core.Gsm(config, self.serial, self.debug)
        self.gsm.sendATMdmDefault("ATE0\r", "OK")

        self.smsManager = core.SmsManager(self.gsm, self.debug)
        self.alarmParser = AlarmParser()
        self.alarmStorage = AlarmStorage()        
        self.recepientHelper = RecepientHelper(self.config, self.gsm, self.debug)

        self.devices = []
        #self.debug.send("Init complete")

    # Возвращает устройства из файла настроек
    def getDevices(self):
        line = self.config.get(GAS_ADDRESS)
        res = []
        for item in line.split(","):
            res.append(int(item))
        
        return res

    # Считывает состояния всех устройств
    def readStates(self, devices):
        # Сканирует сеть
        redevs = {}

        data = []
        for i in xrange(1, 5 + 1):
            self.serial.sendbyte(i, self.speed, '8E1')
            self.serial.sendbyte(0, self.speed, '8E1')

            byte = self.serial.receivebyte(self.speed, "8N1", 0)
            if byte != -1:
                data.append(byte)
            byte = self.serial.receivebyte(self.speed, "8N1", 0)
            if byte != -1:
                data.append(byte)
            
            if len(data) == 2:
                redevs[data[0]] = data[1]
                data = []

        time = MOD.secCounter() + READ_TIMEOUT
        while core.TRUE:
            if MOD.secCounter() > time:
                break
            
            byte = self.serial.receivebyte(self.speed, "8N1", 0)
            if byte != -1:
                data.append(byte)
                if len(data) == 2:
                    redevs[data[0]] = data[1]
                    data = []
                time = MOD.secCounter() + READ_TIMEOUT

        return redevs

    # Обрабатывает слово состояния газоанализатора
    # Возвращает список тревог
    def processState(self, data):
        code = data[1]
        alarms = self.alarmParser.parseOne(code)

        resAlarms = []
        for alarm in alarms:
            rs = self.alarmStorage.add(alarm)
            if rs != None:
                resAlarms.append(rs)

        return resAlarms

    # Отправляет всем
    def sendToRecepients(self, text):
        for recepient in self.recepients:
            self.smsManager.sendSms(recepient, CONNECTED_TEXT)

    # Обрабатывает SMS с
    def processSms(self):
        allSms = self.smsManager.listSms()
        recepients = []
        for sms in allSms:
            for recep in self.recepients:
                if sms.recepient == recep:
                    recepients.append(recep)

        # TODO: последнее состояние
        for rec in recepients:
            self.smsManager.sendSms(rec, "")

        self.smsManager.deleteAll()

    # Запускает
    def start(self):
        #self.debug.send("Start work")
        # Отсылает 10 раз 2 байта переинициализации
        #self.debug.send("Send init bytes")
        for i in xrange(10):
            self.serial.sendbyte(0, self.speed, '8M1')
            self.serial.sendbyte(0, self.speed, '8E1')

        MOD.sleep(REBOOT_WAIT_TIMEOUT)
        
        self.devices = self.getDevices()
        self.recepients = self.recepientHelper.getRecepients()

        self.debug.send(str(self.devices))
        self.debug.send(str(self.recepients))

        # # Отправляет SMS всем получателям что установлена связь
        # if len(self.recepients):
        #     if len(self.devices):
        #         self.sendToRecepients(CONNECTED_TEXT)
        #         self.work()
        #     else:
        #         self.sendToRecepients(NO_CONNECTION_TEXT)

        self.work()

    # Основная работа
    def work(self):
        # self.debug.send("Start work")
        while(core.TRUE):
            # Отсылает запрос состояния каждому газоанализатору
            # TODO: проверка связи и отправка СМС? Что считать за пропадание связи? Связь с одним устройством или со всеми?
            for i in self.devices:
                states = self.readStates(self.devices)
                for item in states.items():
                    self.debug.send(str(item))
                    alarms = self.processState(resp)
                    self.debug.send(str(alarms))
                    for alarm in alarms:
                        txt = str(alarm.code) + " - " + alarm.text
                        self.debug.send(txt)
                        # for recepient in self.recepients:
                        #     self.smsManager.sendSms(recepient, txt)

            self.processSms()

            MOD.sleep(WORK_DELAY)
            break

# Обеспечивает работу в режиме прослушивания БУПС


class BupsWorker:
    # Конструктор
    def __init__(self, config):
        self.speed = config.get(SER_SP)
        self.serial = core.Serial()

        isDebug = config.get(DEBUG_SER) == "1"
        debugSpeed = config.get(DEBUG_SER_SP)
        debugBytetype = config.get(DEBUG_SER_OD)
        self.debug = core.Debug(isDebug, self.serial,
                                debugSpeed, debugBytetype)

        self.gsm = core.Gsm(config, self.serial, self.debug)
        self.gsm.sendATMdmDefault("ATE0\r", "OK")

        self.smsManager = core.SmsManager(self.gsm, self.debug)
        self.alarmStorage = AlarmStorage()
        self.recepientHelper = RecepientHelper(self.config, self.gsm)

    # Запускает
    def start(self):
        self.work()

    # Обрабатывает пакет БУПС
    def processState(self, data):
        return [Alarm(1, "")]

    # Читает байты
    def readBups(self):
        count = 0
        data = []
        byte = 0
        while core.True:
            byte = self.serial.receivebyte(self.speed, "8E1")
            if byte == -1:
                break

            count = count + 1
            data.append(byte)
            if count >= 8:
                break

        if len(data) >= 8:
            return data

    # Основная работа
    def work(self):
        while(core.TRUE):
            # Читает из порта пакеты БУПС
            resp = self.serial.receivebyte(self.speed, "8E1")
            if resp != -1:
                alarms = self.processState(resp)
                # Отсылает СМС адресату
                for alarm in alarms:
                    txt = str(alarm.code) + " - " + alarm.text
                    self.smsManager.sendSms(recepient, txt)

            MOD.sleep(WORK_DELAY)

# Обеспечивает работу в режиме приема СМС и передачи на пульт


class SmsRecieveWorker:
    # Конструктор
    def __init__(self, config):
        self.config = config
        self.serial = core.Serial(config.get(SER_SP))
        self.serial.open()
        self.debug = core.Debug(config.get(DEBUG_SER) == "1", self.serial)
        self.gsm = core.Gsm(config, self.serial, self.debug)
        self.smsManager = core.SmsManager(self.gsm, self.debug)

    # Запускает
    def start(self):
        self.work()

    # Обрабатывает SMS и возвращает описание тревоги
    def processSms(self, sms):
        return Alarm(1, "")

    # Отправляет тревогу
    def sendAlarm(self, alarm):
        self.serial.send("\0\0\0\0\0\0\0")

    # Основная работа
    def work(self):
        while(core.TRUE):
            # Ожидает SMS
            smsList = self.smsManager.listSms()
            for sms in smsList:
                alarm = self.processSms(sms)
                if alarm != None:
                    # Отсылает 4 байта с тревогами на пульт(адрес пульта в INI)
                    self.sendAlarm(alarm)

            self.smsManager.deleteAll()
            MOD.sleep(WORK_DELAY)


try:
    settings = core.IniFile("settings.ini")
    settings.read()

    mode = settings.get(WORK_MODE)
    worker = None
    if mode == DIRECT_MODE:
        worker = DirectWorker(settings)
    elif mode == BUPS_MODE:
        worker = BupsWorker(settings)
    elif mode == SMS_RECIEVE_MODE:
        worker = SmsRecieveWorker(settings)

    worker.start()
except Exception, e:
    import SER
    SER.set_speed("115200", "8N1")
    SER.send(e)
