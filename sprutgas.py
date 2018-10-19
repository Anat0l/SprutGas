import core

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
# Тип байта на серийном порту
SER_OD = "SER_OD"
# Выводить отладку
DEBUG_SER = "DEBUG_SER"
# Режим отправки SMS
SEND_MODE = "SEND_MODE"
# Режим работы
WORK_MODE = "WORK_MODE"

# Максимальный адрес устройства
MAX_ADDRESS = 255

# Задержка в работе
WORK_DELAY = 1

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
    def __init__(self, config, gsm):
        self.config = config
        self.gsm = gsm

    # Возвращает список кому отправить SMS в зависимости от настроек
    def getRecepients(self):
        sendMode = self.config.get(SEND_MODE)
        if sendMode == SEND_MODE_PHONE:
            pass
        elif sendMode == SEND_MODE_MODEM:
            pass

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

# Обеспечивает работу в режиме опроса газовых анализаторов
class DirectWorker:
    # Конструктор
    def __init__(self, config):
        self.config = config

        self.serial = core.Serial(config.get(SER_SP))
        self.serial.open()

        isDebug = config.get(DEBUG_SER) == "1"
        debugSpeed = config.get(DEBUG_SER_SP)
        self.debug = core.Debug(isDebug, self.serial, debugSpeed)
        
        self.gsm = core.Gsm(config, self.serial, self.debug)        
        self.gsm.sendATMdmDefault("ATE0\r", "OK")

        self.smsManager = core.SmsManager(self.gsm, self.debug)        
        self.alarmStorage = AlarmStorage()        
        self.recepientHelper = RecepientHelper(self.config, self.gsm)        

        self.devices = []
        self.debug.send("Init complete")
    
    # Читает состояние с газовых анализаторов
    def readState(self, network):
        self.serial.send(chr(network), '8E1')
        self.serial.send(chr(0), '8E1')
        resp = self.serial.receive(4)
        self.debug.send(resp)
        return resp

    # Обрабатывает слово состояния газоанализатора
    # Возвращает список тревог
    def processState(self, data):
        return [Alarm(1, "")]

    # Запускает
    def start(self):
        self.debug.send("Start work")
        # Отсылает 10 раз 2 байта переинициализации
        self.debug.send("Send init bytes")
        for i in xrange(10):
            self.serial.sendbyte(0, '8O1')
            self.serial.sendbyte(0, '8E1')

        self.debug.send("Scan network")
        # Сканирует сеть
        # self.debug.send("Scan network")
        # resp = self.readState(1)
        # if resp != None:
        #     self.devices.append(1)

        # for i in xrange(MAX_ADDRESS):
        #     resp = self.readState(i)
        #     if resp != None:
        #         self.devices.append(i)

        # self.work()
    
    # Основная работа
    def work(self):
        # self.debug.send("Start work")
        while(core.TRUE):
            recepients = self.recepientHelper.getRecepients()
            if len(recepients) < 1:
                MOD.sleep(WORK_DELAY)
                continue

            # Отсылает запрос состояния каждому газоанализатору
            for i in self.devices:
                resp = readState(i)
                if resp != None:
                    alarms = processState(resp)
                    for alarm in alarms:
                        txt = str(alarm.code) + " - " + alarm.text
                        for recepient in recepients:
                            self.smsManager.sendSms(recepient, txt)
            
            MOD.sleep(WORK_DELAY)
            break

# Обеспечивает работу в режиме прослушивания БУПС
class BupsWorker:
    # Конструктор
    def __init__(self, config):
        self.config = config

        self.serial = core.Serial()
        self.serial.open(config.get(SER_SP), config.get(SER_OD))
        isDebug = config.get(DEBUG_SER) == "1"
        debugSpeed = config.get(DEBUG_SER_SP)
        self.debug = core.Debug(isDebug, self.serial, debugSpeed)
        self.gsm = core.Gsm(config, self.serial, self.debug)
        self.smsManager = core.SmsManager(self.gsm, self.debug)
    
    # Запускает
    def start(self):
        self.work()

    # Ожидает посылки от БУПС
    def readBups(self):
        resp = self.serial.receive(8)
        return resp

    # Обрабатывает пакет БУПС
    def processState(self, data):
        return [Alarm(1, "")]

    # Основная работа
    def work(self):
        while(core.TRUE):            
            # Читает из порта пакеты БУПС
            resp  = self.readBups()
            if resp != None:
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