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

# Кодирует в UCS-2
def encodeUcs2(text):
    s = ''
    i = 0
    while i < len(text):
        c = ord(text[i])
        if c > 128:
            c2 = ord(text[i + 1])
            cod = ('%02X' % c) + ('%02X' % c2)
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

uc = encodeUcs2("1 - Hi")
print(uc)
print(decodeUcs2(uc))