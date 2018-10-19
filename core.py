import SER
import MDM
import MDM2
import MOD

# В старом питоне нет булевского типа
TRUE = 1
FALSE = 0

# Данные INI файла
# Разделитель ::
# Значения ключа хранятся в виде массива
class IniData:
    # data - строка INI файла
    def __init__(self, data = None):
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
    def get(self, k, idx = 0):
        return self.iniData[k][idx]

    # Возвращает массив значений по ключу
    def getAll(self, k):
        return self.iniData[k]

    # Устанавливает значение элемента по ключу и индексу массива
    def set(self, k, v, idx = 0):
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
    def get(self, k, idx = 0):
        return self.data.get(k, idx)

    # Устанавливает значение по ключу
    def set(self, k, v, idx = 0):        
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
    def __init__(self, isDebug, serial, speed):
        self.isDebug = isDebug
        self.serial = serial
        self.speed = speed

    def send(self, msg):
        if (self.isDebug == 1):
            message = str(MOD.secCounter()) + ' # ' + msg + '\r\n'
            self.serial.send(message, "8N1", self.speed)

# Для работы с серийным портом
class Serial:
    def __init__(self, speed):
        self.speed = speed
        self.buffer = ''

    # Открывает порт
    def open(self, bt = "8O1"):
        SER.set_speed(self.speed, bt)

    # Возвращает буффер
    def getBuffer(self, size):
        data = ''
        if(len(self.buffer) > size):
            data = self.buffer[0:size]
            self.buffer = self.buffer[size:]
        else:
            data = self.buffer
            self.buffer = ''
        return data

    # Получить данные из порта
    def receive(self, size):
        data = ''
        while(1):
            rcv = SER.read()
            if(len(rcv) > 0):
                self.buffer = self.buffer + rcv
                if(len(self.buffer) > size):
                    break
            else:
                break

        if(len(self.buffer) > 0):
            data = self.getBuffer(size)

        return data

    # Отправляет данные
    def send(self, data, bt = "8O1", speed = None):
        spd = self.speed
        if speed != None:
            spd = speed
        SER.set_speed(spd, bt)
        SER.send(data)
    
    # Отправляет байт
    def sendbyte(self, byte, bt = "8O1", speed = None):
        spd = self.speed
        if speed != None:
            spd = speed
        SER.set_speed(spd, bt)
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
        # Инициализирует LED
        self.initLed(LED_MODE)

        # Команды инициализации сокета
        socketCommand = 'AT#SCFG=1,1,' + \
            self.config.get('MAX_DATA_LENGTH') + ',90,30,2\r'
        socketCommandExt = 'AT#SCFGEXT=1,1,0,0,0,0\r'

        # Инициализирует сокет
        self.initSocket(socketCommand, socketCommandExt)
        # Инициализирует APN
        self.initApn()

    def initModem(self):
        self.sendATMdmDefault('ATE0\r', 'OK')
        self.sendATMdmDefault('AT\\R0\r', 'OK')
        self.sendATMdmDefault(
            'AT#ENHRST=2,' + self.config.get('REBOOT_PERIOD') + '\r', 'OK')

        # Устанавливает скорость работы
        speed = self.config.get('SER_SP')
        atCommand = "AT+IPR=" + speed + "\r"
        self.debug.send(atCommand)
        self.sendATMdmDefault(atCommand, 'OK')

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

    # Устанавливает параметры LED
    def initLed(self, mode, onDur = None, offDur = None):
        val = str(mode)
        if onDur != None:
            val = val + ',' + str(onDur)
            if offDur != None:
                val = val + ',' + str(offDur)
                
        self.sendATMdmAndWait('AT#SLED='+ val +'\r', 'OK')
        self.sendATMdmAndWait('AT#SLEDSAV\r', 'OK')

    # Инициализирует режим запуска
    def initStartMode(self):
        mode = self.config.get('STARTMODESCR')
        self.sendATMdmDefault('AT#STARTMODESCR=' + mode + '\r', 'OK')
        self.debug.send('initStartMode() passed OK')

    # Инициализирует APN
    def initApn(self):
        apn = self.config.get('APN')

        # Если автоматическое определение
        if self.config.get('APN_SETTINGS') == '1':
            self.debug.send("Detecting APN")
            # Читает IMSI
            at_timeout = int(self.config.get('TIMEOUT_AT'))
            a, s = self.sendATMdmAndWait('AT#CIMI\r', 'OK', 10, at_timeout)
            if (a < 0):
                raise Exception, 'Regular. initContext() failed'
            imsi = s.split(" ")[1]
            operator = imsi[3:5]
            self.apnInfo = self.apnResolver.get(operator)
            if self.apnInfo != None:
                apn = self.apnInfo.apn
                self.debug.send("APN Detected: " + apn)

        self.debug.send("Using APN: " + apn)
        self.sendATMdmDefault('AT+CGDCONT=1,"IP","' + apn + '"\r', 'OK')

    # Активирует GPRS
    def activateGprs(self):
        timeout = int(self.config.get('TIMEOUT_PDP'))
        a, s = self.sendATMdmAndWait('AT#SGACT=1,0\r', 'OK', 5, timeout)
        if (a == 0):
            user = self.config.get('GPRS_USER')
            password = self.config.get('GPRS_PASSWD')
            if self.apnInfo != None:
                user = self.apnInfo.user
                password = self.apnInfo.password

            a, s = self.sendATMdmAndWait('AT#SGACT=1,1,"' + user +
                                         '","' + password + '"\r', 'OK', 10, timeout)
            if (a == 0):
                str_IP = s.split(chr(13))
                i_str_IP = str_IP[1].find(': ')
                My_IP = str_IP[1][i_str_IP + 2:]
                self.debug.send('GPRS CONTEXT activated ... OK  IP: ' + My_IP)
                return My_IP
        raise Exception, 'Regular. Activate GPRS CONTEXT failed'

    # Проверяет GPRS
    def checkGprs(self):
        timeout = int(self.config.get('TIMEOUT_MDM'))
        a, s = self.sendATMdmAndWait('AT#SGACT?\r', 'OK', 10, timeout)
        d = s.find('#SGACT:')
        if (d != -1):
            if (s[d + 10]) == '1':
                return TRUE
        return FALSE

    # Инициализирует сокер
    def initSocket(self, scfg, scfgext):
        self.sendATMdmDefault(scfg, 'OK')
        self.sendATMdmDefault(scfgext, 'OK')
        self.debug.send('initSocket() passed OK')

    # Открывает подключение к серверу
    def connect(self, socket, ip, port, trys):
        timeout = int(self.config.get('TIMEOUT_TCP'))
        if(socket == '1'):
            a, s = self.sendATMdm2AndWait(
                'AT#SD=' + socket + ',0,' + port + ',"' + ip + '",0,1,0\r', 'CONNECT', trys, timeout)
        else:
            a, s = self.sendATMdm2AndWait('AT#SD=' + socket + ',0,' + port +
                                          ',"' + ip + '",0,1,1\r', 'OK', trys, timeout)
        if (a < 0):
            raise Exception, 'Regular. TCP connection on socket'
        self.debug.send('Socket ' + socket +
                        ' connected to ' + ip + ':' + port)

    # Проверка доступности узла
    def ping(self, ip):
        timeout = int(self.config.get('TIMEOUT_TCP'))
        a, s = self.sendATMdmAndWait('AT#PING="' + ip + '",1,32,' +
                                     self.config.get('PING_TIMEOUT') + ',128\r', 'OK', 1, timeout)
        if ((a < 0) or (s.find('600,255') != -1)):
            self.debug.send('ERROR. ping() to ' + ip + ' failed')
            return (-1)
        self.debug.send('ping() to ' + ip + ' OK')
        return (0)

    def checkSocket(self, socket):
        timeout = int(self.config.get('TIMEOUT_MDM'))
        a, s = self.sendATMdmAndWait(
            'AT#SS=' + socket + '\r', 'OK', 10, timeout)
        d = s.find('#SS:')
        if (d != -1):
            return(s[d + 7])
        raise Exception, 'Regular. checkSocket() failed'

    # Получает IMEI
    def getImei(self):
        a, s = self.sendATMdmDefault('AT+CGSN\r', 'OK')
        self.debug.send('IMEI RAW: ' + s)
        if(a < 0):
            self.debug.send('ERROR. getImei() failed')
            return '0'
        imei = s.strip()[:15]
        return imei

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
        size = int(self.config.get('MAX_DATA_LENGTH'))
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
        self.gsm.sendATMdmDefault("AT+CMGF=1\r", "OK")               # Текстовый режим
        self.gsm.sendATMdmDefault("AT+CNMI=1,0\r", "OK")             # Блокирует сигнализацию получения СМС
        self.gsm.sendATMdmDefault("AT+CSCS=GSM\r", "OK")             # Устанавливает формат GSM как основной charset
        self.gsm.sendATMdmDefault("AT+CSMP=1,167,0,8\r", "OK")
        self.debug.send("Sms context initialized")

    # Отправляет СМС
    def sendSms(self, recepient, text):
        self.gsm.sendATMdmDefault('AT+CMGS="' + recepient +'",145\r', ">")
        self.gsm.sendATMdm(text)
        self.gsm.sendATMdmDefault('\x1a', "OK") # отсылает CTRL+Z

    # Возвращает список новых СМС
    def listSms(self):
        self.debug.send("listSms")
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
                recepient = headerDataItems[2]
                data = items[i].strip()
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