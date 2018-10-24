TRUE = 1
FALSE = 0

# Описание тревоги
class Alarm:
    # Конструктор
    # code - код тревоги    
    # txt - текстовое описание
    # state - состояние: вкл/откл
    def __init__(self, code, text, state = TRUE):
        self.code = code
        self.state = state
        self.text = text

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
            alarms.append(Alarm(8, "Клапан открыт"))
        if (code & 0x10 > 0):
            alarms.append(Alarm(9, "Клапан закрыт"))
        
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

parser = AlarmParser()
alarm = parser.parseOne(64)
print(alarm[0].code)
print(alarm[0].text)