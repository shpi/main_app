import struct

def devloop(devpath):
    systembits = (struct.calcsize("P") * 8)
    with open(devpath, 'rb') as devfile:
     while True:
        event = devfile.read(16 if systembits == 32 else 24)  #16 byte for 32bit,  24 for 64bit
        (_timestamp, _id, code, type, value) = struct.unpack('llHHI', event)
        print(str(_timestamp) + '  ' +  str(code) + ' '  + str(type) + ' : '  +  str(value))



devloop('/dev/input/event5')
