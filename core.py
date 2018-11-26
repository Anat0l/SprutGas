import SER
import MDM
import MDM2
import MOD

# В старом питоне нет булевского типа
TRUE = 1
FALSE = 0

# Максимальная длина принимаемого сообщения
MAX_DATA_LENGTH = 1500

SYMBOLS = {
    "D090": 1040, "D091": 1041, "D092": 1042, "D093": 1043, "D094": 1044, "D095": 1045,
    "D081": 1025, "D096": 1046, "D097": 1047, "D098": 1048, "D099": 1049, "D09A": 1050,
    "D09B": 1051, "D09C": 1052, "D09D": 1053, "D09E": 1054, "D09F": 1055, "D0A0": 1056,
    "D0A1": 1057, "D0A2": 1058, "D0A3": 1059, "D0A4": 1060, "D0A5": 1061, "D0A6": 1062,
    "D0A7": 1063, "D0A8": 1064, "D0A9": 1065, "D0AA": 1066, "D0AB": 1067, "D0AC": 1068,
    "D0AD": 1069, "D0AE": 1070, "D0AF": 1071, "D0B0": 1072, "D0B1": 1073, "D0B2": 1074,
    "D0B3": 1075, "D0B4": 1076, "D0B5": 1077, "D191": 1105, "D0B6": 1078, "D0B7": 1079,
    "D0B8": 1080, "D0B9": 1081, "D0BA": 1082, "D0BB": 1083, "D0BC": 1084, "D0BD": 1085,
    "D0BE": 1086, "D0BF": 1087, "D180": 1088, "D181": 1089, "D182": 1090, "D183": 1091,
    "D184": 1092, "D185": 1093, "D186": 1094, "D187": 1095, "D188": 1096, "D189": 1097,
    "D18A": 1098, "D18B": 1099, "D18C": 1100, "D18D": 1101, "D18E": 1102, "D18F": 1103
}

# Возвращает количество бит в числе
# По умолчанию возвращает для байта
def getBitCount(number, count=8):
    res = 0
    for i in xrange(0, count):
        if (number & pow(2, i)) > 0:
            res = res + 1
    return res

# Проверяет является ли число не чётным
def isOdd(byte):
    count = getBitCount(byte)
    if (count % 2 > 0):
        return TRUE
    return FALSE

# Кодирует в UCS-2
def encodeUcs2(text):
    s = ''
    i = 0
    while i < len(text):
        c = ord(text[i])
        if c > 128:
            c2 = ord(text[i + 1])
            cod = ('%02X' % c) + ('%02X' % c2)
            # print(cod)
            c = SYMBOLS[cod]
            i = i + 1

        s = s + '%04X' % c
        i = i + 1

    return s

# Декодирует из UCS-2
def decodeUcs2(text):
    count = len(text) / 4
    res = []
    for i in xrange(0, count):
        pos = i * 4
        first = int(text[pos] + text[pos + 1], 16)
        second = int(text[pos + 2] + text[pos + 3], 16)
        full = (first << 8) + second
        if first == 0:
            res.append(chr(second))

    return "".join(res)

# Данные INI файла
# Разделитель ::
# Значения ключа хранятся в виде массива
class IniData:
    # data - строка INI файла
    def __init__(self, data=None):
        self.iniData = {}

        if data != None:
            lines = data.split("\n")
            for l in lines:
                kv = l.strip().split('::')
                key = kv[0].strip()
                if len(key) < 1:
                    continue
                vals = []
                items = kv[1:]
                for it in items:
                    vals.append(it.strip())

                self.iniData[key] = vals

    # Возвращает есть ли значение по ключу
    def exists(self, k):
        return self.iniData.has_key(k)

    # Получает значение элемента из массива по ключу и индексу массива
    def get(self, k, idx=0):
        return self.iniData[k][idx]

    # Возвращает массив значений по ключу
    def getAll(self, k):
        return self.iniData[k]

    # Устанавливает значение элемента по ключу и индексу массива
    def set(self, k, v, idx=0):
        vals = []
        if self.iniData.has_key(k):
            vals = self.iniData[k]
        else:
            self.iniData[k] = vals

        ln = idx + 1
        if ln >= len(vals):
            cnt = ln - len(vals)
            for i in xrange(cnt):
                vals.append('')

        vals[idx] = str(v)

    # Устанавливает все значения по ключу
    def setAll(self, k, v):
        self.iniData[k] = v

    # Очищает данные
    def clear(self):
        self.iniData.clear()

# Для работы с файлами INI
class IniFile:
    # name - название файла
    def __init__(self, name):
        self.data = IniData()
        self.name = name

    # Получает значение по ключу
    def get(self, k, idx=0):
        return self.data.get(k, idx)

    # Устанавливает значение по ключу
    def set(self, k, v, idx=0):
        self.data.set(k, v, idx)

    # Читает настройки из файла
    def read(self):
        fh = open(self.name, "r")
        try:
            self.data = IniData(fh.read())
        finally:
            fh.close()

    # Записывает настройки
    def write(self):
        fh = open(self.name, "w")
        try:
            iniData = self.data.iniData
            if len(iniData.keys()) > 0:
                lines = []
                for k in iniData.keys():
                    data = '::'.join(iniData[k])
                    lines.append(str(k) + '::' + data + '\n')
                fh.writelines(lines)
            else:
                fh.write(" ")
        finally:
            fh.close()
            flashflush()

    # Возвращает все ключи
    def keys(self):
        res = []
        for key in self.iniData().keys():
            res.append(key)
        return res

    # Проверяет есть ли значение по ключу
    def exists(self, k):
        return self.data.exists(k)

    # Возвращает количество элементов
    def count(self):
        return len(self.iniData().values())

    # Очищает данные
    def clear(self):
        self.data.clear()

    # Возвращает данные ини файла
    def iniData(self):
        return self.data.iniData

# Для вывода отладки
class Debug:
    # isDebug: 1 - выводить сообщение, 0 - не выводить
    def __init__(self, isDebug, serial, speed, bytetype):
        self.isDebug = isDebug
        self.serial = serial
        self.speed = speed
        self.bytetype = bytetype

    # Отправляет в отладку сообщение
    def send(self, msg):
        if (self.isDebug == 1):
            message = str(MOD.secCounter()) + ' # ' + msg + '\r\n'
            self.serial.send(message, self.speed, self.bytetype)

    # Отправляет в отладку байт
    def sendbyte(self, byte):
        if (self.isDebug == 1):
            self.serial.send(str(MOD.secCounter()) + ' # ',
                             self.speed, self.bytetype)
            self.serial.sendbyte(byte, self.speed, self.bytetype)
            self.serial.send('\r\n', self.speed, self.bytetype)

# Для работы с серийным портом
class Serial:
    def __init__(self):
        self.buffer = ''
        self.lastSpeed = ''
        self.lastBt = ''

    # Открывает порт
    def open(self, speed, bt):
        if (self.lastSpeed != speed) or (self.lastBt != bt):
            rs = SER.set_speed(speed, bt)
            if rs == -1:
                raise Exception, 'Regular. port open failed'
            self.lastBt = bt
            self.lastSpeed = speed

    # Возвращает массив данных, полученных в течении времени(timeout)
    def receive(self, speed, bt, timeout=1):
        self.open(speed, bt)
        return SER.receive(timeout)

    # Считывает один байт пока не придут данные
    def receivebyte(self, speed, bt):
        self.open(speed, bt)
        return SER.receivebyte()

    # Считывает один байт с таймаутом
    def receivebyte(self, speed, bt, timeout=0):
        self.open(speed, bt)
        return SER.receivebyte(timeout)

    # Отправляет данные
    def send(self, data, speed, bt):
        self.open(speed, bt)
        SER.send(data)

    # Отправляет байт
    def sendbyte(self, byte, speed, bt):
        self.open(speed, bt)
        SER.sendbyte(byte)

# Для работы с модемом через AT команды
# Отрефакторить, много мусора
class Gsm:
    def __init__(self, config, serial, debug):
        self.config = config
        self.debug = debug
        self.serial = serial
        self.buffer = ''
        self.apnInfo = None
        self.disableRing = TRUE
        # Обратный вызов при получении звонка
        self.onRing = None

    # Устанавливает обратный вызов на входящий RING
    def setOnRing(self, onRing):
        self.onRing = onRing

    # Reboot modem
    def reboot(self):
        self.debug.send("Start reboot")
        self.sendATMdmDefault('AT#ENHRST=1,0\r', 'OK')
        MOD.sleep(10)
        sys.exit(None)

    # Отсылает AT команду через MDM и не ждёт ответа
    def sendATMdm(self, atcom):
        mdm_timeout = int(self.config.get('TIMEOUT_MDM'))
        MDM.send(atcom, mdm_timeout)
        self.debug.send('DATA AT OUT: ' + atcom)

    # Отсылает AT команду через MDM2 и не ждёт ответа
    def sendATMdm2(self, atcom):
        mdm_timeout = int(self.config.get('TIMEOUT_MDM'))
        MDM2.send(atcom, mdm_timeout)
        self.debug.send('DATA AT OUT: ' + atcom)

    # Проверяет наличие RING
    def checkOnRing(self, mdm, data):
        if (data != None) and (data != '') and (data.find(RING) >= 0):
            if self.disableRing == TRUE:
                # Завершает звонок
                self.sendATAndWait(mdm, "ATH", "OK")
            else:
                if self.onRing != None:
                    self.onRing()

    # Отсылает команду через и ждёт указанного ответа
    def sendATAndWait(self, mdm, atcom, atres, trys=1, timeout=1):
        mdm_timeout = int(self.config.get('TIMEOUT_MDM'))
        s = mdm.receive(mdm_timeout)
        result = -2
        while(1):
            self.debug.send('DATA AT OUT: ' + atcom)
            s = ''
            mdm.send(atcom, mdm_timeout)
            timer = MOD.secCounter() + timeout
            while(1):
                s = s + mdm.receive(mdm_timeout)
                if(s.find(atres) != -1):
                    result = 0
                    break
                if(s.find('ERROR') != -1):
                    result = -1
                    break
                if(MOD.secCounter() > timer):
                    break
            self.debug.send('DATA AT IN: ' + s[2:])
            trys = trys - 1
            if((trys <= 0) or (result == 0)):
                break
            MOD.sleep(15)

        return (result, s)

    # Отсылает команду через MDM и ждёт указанного ответа
    def sendATMdmAndWait(self, atcom, atres, trys=1, timeout=1):
        return self.sendATAndWait(MDM, atcom, atres, trys, timeout)

    # Отсылает команду через MDM2 и ждёт указанного ответа
    def sendATMdm2AndWait(self, atcom, atres, trys=1, timeout=1):
        return self.sendATAndWait(MDM2, atcom, atres, trys, timeout)

    # Отсылает запрос в MDM и ждёт ответа
    def sendATMdmDefault(self, request, response):
        at_timeout = int(self.config.get('TIMEOUT_AT'))
        a, s = self.sendATMdmAndWait(request, response, 1, at_timeout)
        if (a < 0):
            raise Exception, 'Regular. sendATMdmAndWait()'

        return a, s

    # Отсылает запрос в MDM2 и ждёт ответа
    def sendATMdm2Default(self, request, response):
        at_timeout = int(self.config.get('TIMEOUT_AT'))
        a, s = self.sendATMdm2AndWait(request, response, 1, at_timeout)
        if (a < 0):
            raise Exception, 'Regular. sendATMdmAndWait()'

        return a, s

    # Полностью инициализирует модем
    def simpleInit(self):
        # Инициализирует модем
        self.initModem()
        # Инициализирует SIM карту
        self.initSim()
        # Проверяет инициализацию в сети
        self.initCreg()
        # Получает уровень сигнала
        self.initCsq()

    def initModem(self):
        self.sendATMdmDefault('ATE0\r', 'OK')
        self.sendATMdmDefault('AT\\R0\r', 'OK')
        self.sendATMdmDefault(
            'AT#ENHRST=2,' + self.config.get('REBOOT_PERIOD') + '\r', 'OK')

        self.debug.send('initModem() passed OK')

    # Инициализирует SIM карту
    def initSim(self):
        at_timeout = int(self.config.get('TIMEOUT_AT'))
        a, s = self.sendATMdmAndWait('AT+CPIN?\r', 'READY', 3, at_timeout)
        if (a < 0):
            a, s = self.sendATMdmAndWait(
                'AT+CPIN?\r', 'SIM PIN', 3, at_timeout)
            if(a == 0):
                a, s = self.sendATMdmAndWait(
                    'AT+CPIN=' + self.config.get('PIN') + '\r', 'OK', 3, at_timeout)
                if (a == 0):
                    a, s = self.sendATMdmAndWait(
                        'AT+CPIN?\r', 'READY', 3, at_timeout)
                    if (a < 0):
                        raise Exception, 'Regular. initSim() failed'
                else:
                    raise Exception, 'Regular. initSim() failed'
            else:
                raise Exception, 'Regular. initSim() failed'
        self.debug.send('initSim() passed OK')

    # Проверяет регистрацию в сети
    def initCreg(self):
        at_timeout = int(self.config.get('TIMEOUT_AT'))
        a, s = self.sendATMdmAndWait(
            'AT+CREG?\r', '+CREG: 0,1', 10, at_timeout)
        if (a < 0):
            raise Exception, 'Regular. initCreg() failed'
        self.debug.send('initCreg() passed OK')

    # Возвращает уровень сигнала
    def getSignal(self):
        at_timeout = int(self.config.get('TIMEOUT_AT'))
        a, s = self.sendATMdmAndWait('AT+CSQ\r', 'OK', 3, at_timeout)
        if (a < 0):
            raise Exception, 'Regular. initCsq() failed'

        res = s.split(" ")[1].split(",")[0]
        return res

    # Выводит уровень сигнала
    def initCsq(self):
        sig = self.getSignal()
        self.debug.send('initCsq() passed OK ' + sig)

    # Возвращает буффер с данными
    def getBuffer(self, size):
        data = ''
        if(len(self.buffer) > size):
            data = self.buffer[0:size]
            self.buffer = self.buffer[size:]
        else:
            data = self.buffer
            self.buffer = ''
        return data

    # Получает данные от модема
    def receiveData(self, mdm):
        data = ''
        size = MAX_DATA_LENGTH
        while(1):
            rcv = mdm.read()
            if(len(rcv) > 0):
                self.buffer = self.buffer + rcv
                if(len(self.buffer) > size):
                    break
            else:
                break
        if(len(self.buffer) > 0):
            data = self.getBuffer(size)
            self.debug.send(
                'Received: ' + str(len(data)) + ' bytes')

        return data

    # Читает из MDM данные
    def receiveMdm(self):
        return self.receiveData(MDM)

    # Читает из MDM2 данные
    def receiveMdm2(self):
        return self.receiveData(MDM2)

    # Читает из MDM сообщение заданной длины
    def receiveMdmLength(self, length):
        s = ''

        while(1):
            s = s + self.receiveMdm()
            if len(s) >= length:
                break

        return s[:length]

    # Читает из MDM2 сообщение заданной длины
    def receiveMdm2Length(self, length):
        s = ''

        while(1):
            s = s + self.receiveMdm2()
            if len(s) >= length:
                break

        return s[:length]

    # Отсылает сырые данные в MDM
    def sendMdm(self, data):
        MDM.send(data, 50)
        self.debug.send('Sending data to MDM: ' +
                        str(len(data)) + ' bytes')

    # Отсылает сырые данные в MDM2
    def sendMdm2(self, data):
        MDM2.send(data, 50)
        self.debug.send('Sending data MDM2: ' + str(len(data)) + ' bytes')

# Данные СМС
class SmsData:
    def __init__(self, id, recepient, text):
        self.id = id
        self.recepient = recepient
        self.text = text

# Для работы с СМС
class SmsManager:
    def __init__(self, gsm, debug):
        self.gsm = gsm
        self.debug = debug

    # Инициализирует контект
    def initContext(self, isTextMode=TRUE):
        self.debug.send("Start ini sms context")
        self.gsm.sendATMdmDefault("AT#SMSMODE=1\r", "OK")
        # Текстовый режим
        self.gsm.sendATMdmDefault("AT+CMGF=1\r", "OK")
        # Блокирует сигнализацию получения СМС
        self.gsm.sendATMdmDefault("AT+CNMI=1,0\r", "OK")
        # Устанавливает формат GSM как основной charset
        self.gsm.sendATMdmDefault("AT+CSCS=GSM\r", "OK")
        self.gsm.sendATMdmDefault("AT+CSMP=1,167,0,8\r", "OK")
        self.debug.send("Sms context initialized")

    # Отправляет СМС
    def sendSms(self, recepient, text):
        recepient = recepient.replace("+7", "8")
        self.gsm.sendATMdmDefault('AT+CMGS="' + recepient + '",129\r', ">")
        txt = encodeUcs2(text)
        self.gsm.sendATMdm(txt)
        self.gsm.sendATMdmDefault('\x1a', "OK")  # отсылает CTRL+Z

    # Возвращает список новых СМС
    def listSms(self):
        self.debug.send("List Sms")
        self.gsm.sendATMdm('AT+CMGL="ALL"\r')
        lst = []
        strData = ""

        data = self.gsm.receiveMdm()
        while len(data) > 0:
            strData = strData + data
            data = self.gsm.receiveMdm()

        items = strData.split('\r\n')
        i = 0
        while i < len(items):
            item = items[i]
            txt = item.strip()
            if len(txt) < 1:
                i = i + 1
                continue

            headerItems = txt.split("+CMGL: ")
            # Если заголовок найден
            if (len(headerItems) > 1):
                headerDataItems = headerItems[1].split(",")
                id = int(headerDataItems[0])
                i = i + 1
                recepient = headerDataItems[2].replace('"', "")
                data = items[i].strip()
                data = decodeUcs2(data)
                sms = SmsData(id, recepient, data)
                lst.append(sms)

            i = i + 1

        self.debug.send("Recieved " + str(len(lst)) + " SMS")
        return lst

    # Ищет СМС по тексту, удаляет найденное если нужно
    def findSmsByText(self, textFilter, deleteFound=TRUE):
        smsList = self.listSms()
        res = []
        for sms in smsList:
            for filter in textFilter:
                if sms.text.find(filter) >= 0:
                    res.append(sms)

        if deleteFound == TRUE:
            for sms in res:
                self.deleteSms(sms.id)

        return res

    # Удаляет сообщение по индексу
    def deleteSms(self, idx):
        self.debug.send("Delete sms")
        self.gsm.sendATMdm('AT+CMGD=' + str(idx) + '\r')

    # Удаляет все СМС
    def deleteAll(self):
        smsList = self.listSms()
        for smsData in smsList:
            self.deleteSms(smsData.id)
