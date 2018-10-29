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
# Таймаут отсутствия связи
CONNECTION_TIMEOUT = 60 * 3
# Таймаут ожидания запуска после рестарта
REBOOT_WAIT_TIMEOUT = 100

# Задержка в работе
WORK_DELAY = 1

# Текст сообщений
NO_CONNECTION_TEXT = "Нет связи с системой СГК"
CONNECTED_TEXT = "Связь с системой СГК установлена"
NO_DEVICES = "Не заданы устройства"

# Коды тревог
CLAPAN_OPENED = 8
CLAPAN_CLOSED = 9

# Информация об устройстве и его состоянии
class DeviceInfo:
    # Конструктор
    def __init__(self, network):
        self.network = network
        self.connected = core.FALSE
        self.onConnectionTimeout = 0
    
    def __str__(self):
        return str(self.network)

# Описание тревоги
class Alarm:
    # Конструктор
    # code - код тревоги    
    # txt - текстовое описание
    # state - состояние: вкл/откл
    def __init__(self, code, text, state = core.TRUE):
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

    # Сравнивает
    def add(self, alarms):
        res = []  # Снятые тревоги
        # Ищет снятые тревоги
        for item in self.alarms.items():
            key = item[0]
            storedAlarm = item[1]
            found = core.FALSE
            for inAlarm in alarms:
                if inAlarm.code == storedAlarm.code:
                    found = core.TRUE
                    break
            
            # Сохранённая тревога не найдена == снятие тревоги
            if found == core.FALSE:
                res.append(Alarm(storedAlarm.code, storedAlarm.text, core.FALSE))
        
        # Удаляет снятые тревоги
        for alarm in res:
            del self.alarms[alarm.code]

        # Ищет установленные тревоги
        for inAlarm in alarms:
            if not self.alarms.has_key(inAlarm.code):
                alarm = Alarm(inAlarm.code, inAlarm.text)
                self.alarms[inAlarm.code] = alarm
                res.append(alarm)

        return res

# Парсер тревог полученных от устройства
class AlarmParser:
    def __init__(self):
        pass

    # Парсит тревоги газ анализаторов и первый байт бупса
    def parseOne(self, code):
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
            alarms.append(Alarm(CLAPAN_OPENED, "Клапан открыт"))
        else:
            alarms.append(Alarm(CLAPAN_CLOSED, "Клапан закрыт"))
        
        return alarms

    # Парсит тревоги из второго байта бупс
    def parseTwo(self, code):
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
    def parseThree(self, code):
        # Не нужен пока что
        pass

    # Парсит тревоги из четвёртого байта бупс
    def parseFour(self, code):
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
        self.gsm.simpleInit()

        self.smsManager = core.SmsManager(self.gsm, self.debug)
        self.smsManager.initContext()
        self.smsReadTimer = 0
        self.resetSmsTimer()

        self.alarmParser = AlarmParser()
        self.alarmStorage = AlarmStorage()        
        self.recepientHelper = RecepientHelper(self.config, self.gsm, self.debug)
        self.globalConnected = None
        # Таймаут отсутствия связи в неопределенном состоянии
        self.onConnectionTimeout = MOD.secCounter() + CONNECTION_TIMEOUT

        self.devices = []
        self.initWatchdog()

    # Сбрасывает таймер чтения СМС
    def resetSmsTimer(self):
        self.smsReadTimer = MOD.secCounter() + int(self.config.get('SMS_READ_PERIOD'))

    # Инициализирует охранный таймер
    def initWatchdog(self):
        MOD.watchdogEnable(int(self.config.get('WATCHDOG_PERIOD')))

    # Сбрасывает охранный таймер
    def resetWatchdog(self):
        MOD.watchdogReset()        

    # Возвращает устройства из файла настроек
    def getDevices(self):
        line = self.config.get(GAS_ADDRESS)
        res = []
        for item in line.split(","):
            dev = DeviceInfo(int(item))
            dev.onConnectionTimeout = MOD.secCounter() + CONNECTION_TIMEOUT
            res.append(dev)
        
        return res

    # Считывает состояния всех устройств
    def readStates(self, devices):
        redevs = {}

        data = []
        for dev in devices:
            self.serial.sendbyte(dev.network, self.speed, '8E1')
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
        resAlarms = self.alarmStorage.add(alarms)
        return resAlarms

    # Отправляет всем
    def sendToRecepients(self, text):
        for recepient in self.recepients:
            self.debug.send("SEND ALARM TO RECEPIENTS")
            self.smsManager.sendSms(recepient, CONNECTED_TEXT)            
            #self.debug.send(text)

    # Обрабатывает SMS с командой
    def processSms(self):
        self.debug.send("Process SMS")

        if MOD.secCounter() < self.smsReadTimer:
            self.debug.send("Wait for SMS read")
            return

        allSms = self.smsManager.listSms()
        recepients = []
        for sms in allSms:
            for recep in self.recepients:
                if sms.recepient == recep:
                    recepients.append(recep)
        
        self.debug.send(str(recepients))
        count = len(self.alarmStorage.alarms)
        txt = ""
        # Клапан или открыт или закрыт
        if count == 0:
            txt = "Состояние неизвестно"
        elif count == 1:
            alarm = self.alarmStorage.alarms.items()[0][1]
            txt = "Аварий нет. " + alarm.text
        else:
            clapanIsOpen = core.FALSE
            for item in self.alarmStorage.alarms.items():
                alarm = item[1]
                if alarm.code == CLAPAN_OPENED:
                    clapanIsOpen = core.TRUE
                elif alarm.code == CLAPAN_CLOSED:
                    clapanIsOpen = core.FALSE
                else:
                    txt = txt + alarm.text + ", "
            
            if clapanIsOpen == core.TRUE:
                txt = txt + "Клапан открыт"
            else:
                txt = txt + "Клапан закрыт"                    

        for rec in recepients:
            self.smsManager.sendSms(rec, txt)

        self.smsManager.deleteAll()
        self.resetSmsTimer()

    # Проверяет есть ли связь. Отсылает SMS если не было связи в течении 3-х минут
    # Или отсылает SMS что связь появилась
    def checkConnection(self, states):
        self.debug.send("Check connection")
        self.debug.send(str(len(states)))

        for network in states.keys():
            found = core.FALSE
            for dev in self.devices:
                if network == dev.network:
                    found = core.TRUE
                    break
                        
            dev.connected = found
            if found == core.TRUE:
                dev.onConnectionTimeout = MOD.secCounter() + CONNECTION_TIMEOUT
            else:
                # Таймаут превышен
                if MOD.secCounter() >= dev.onConnectionTimeout:
                    dev.connected = core.FALSE

        connected = core.TRUE
        for dev in self.devices:
            if dev.connected == core.FALSE:
                connected = core.FALSE
                break

        self.debug.send("Connected: " + str(connected))
        self.debug.send("Global Connected: " + str(self.globalConnected))
        
        # Если неопределённое состояние
        if self.globalConnected == None:
            if (connected == core.FALSE) and (MOD.secCounter() > self.onConnectionTimeout):
                self.sendToRecepients(NO_CONNECTION_TEXT)
                self.globalConnected = core.FALSE
            elif connected == core.TRUE:
                self.sendToRecepients(CONNECTED_TEXT)
                self.globalConnected = core.TRUE
        # Если находится в состоянии подключения
        # Отсылает СМС и устанавливает состояние не соединено
        elif self.globalConnected == core.TRUE:
            if connected == core.FALSE:
                self.sendToRecepients(NO_CONNECTION_TEXT)
                self.globalConnected = core.FALSE
        # Если не подключен
        else:
            if connected == core.TRUE:
                self.sendToRecepients(CONNECTED_TEXT)
                self.globalConnected = core.TRUE

    # Запускает
    def start(self):
        # Отсылает 10 раз 2 байта переинициализации        
        for i in xrange(10):
            self.serial.sendbyte(0, self.speed, '8M1')
            self.serial.sendbyte(0, self.speed, '8E1')

        MOD.sleep(REBOOT_WAIT_TIMEOUT)
        
        self.devices = self.getDevices()
        self.recepients = self.recepientHelper.getRecepients()

        self.debug.send(str(self.devices))
        self.debug.send(str(self.recepients))

        # Отправляет SMS всем получателям что установлена связь
        if len(self.recepients) > 0:
            if len(self.devices) > 0:                
                self.work()
            else:
                self.sendToRecepients(NO_DEVICES)

    # Основная работа
    def work(self):
        # self.debug.send("Start work")
        while(core.TRUE):
        #for x in xrange(1, 3):
            # Отсылает запрос состояния каждому газоанализатору
            states = self.readStates(self.devices)
            # Проверяет есть ли связь. Отсылает SMS если не было связи в течении 3-х минут
            # Или отсылает SMS что связь появилась
            self.checkConnection(states)

            self.debug.send("STATES COUNT: " + str(len(states)))
            for item in states.items():
                self.debug.send(str(item))
                alarms = self.processState(item)
                self.debug.send("ALARMS COUNT: " + str(len(alarms)))
                for alarm in alarms:
                    txt = str(alarm.code) + " - " + alarm.text
                    self.sendToRecepients(txt)

            # Получает СМС и отправляет последнее состояние
            self.processSms()
            # Сбрасывает охранный таймер
            self.resetWatchdog()

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
