import SER
import SER2

for x in xrange(10):
    SER.set_speed("115200", "8N1")
    SER.send("GOOD")
    SER.set_speed("9600", "8O1")
    SER.sendbyte(0)
    SER.set_speed("9600", "8E1")
    SER.sendbyte(0)    

# res = SER.receive(10)
# SER.send(res)
