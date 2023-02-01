import serial
from dynamixel_sdk import *                 # Uses Dynamixel SDK library
import argparse
import struct
import time
import sys
#import test_lcd

# Protocol version
PROTOCOL_VERSION        = 1.0               # See which protocol version is used in the Dynamixel
# Default setting
DXL_ID                  = 1                 # Dynamixel ID : 1
BAUDRATE                = 1000000             # Dynamixel default baudrate : 57600
#DEVICENAME              = 'COM8'    # Check which port is being used on your controller

MODEL_BALL     = (0x02)
MODEL_BUT      = (0x03)
MODEL_DRIVE1   = (0x05)
MODEL_DRIVE2   = (0x06)
MODEL_ENCODER  = (0x07)
MODEL_LED      = (0x09)
MODEL_POT      = (0x13)
MODEL_RGB      = (0x15)
MODEL_MOS      = (0x11)
MODEL_ZUMMER   = (0x18)
MODEL_NOISE    = (0x12)
MODEL_LINE     = (0x0A)
MODEL_USW      = (0x17)
MODEL_IR       = (0x08)
MODEL_COLOR    = (0x04)
MODEL_FORCE    = (0x20)
MODEL_PRESS    = (0x14)
MODEL_TEMP     = (0x16)
MODEL_LIGHT    = (0x19)
MODEL_MEMS     = (0x10)
MODEL_MEMS2    = (0x30)
MODEL_AUDIO    = (0x01)
MODEL_XFACE    = (0xA1)
MODEL_ULTRASONIC = (0x2A)
MODEL_ZIGBEE = (0x80)
MODEL_AX_S1 = (0x0D)

class SensorRegTest(object):
    def __init__(self, test_type, addr, val = 0, accuracy = 0, info = '', duration = 1, watch_accuracy = -1):
        self.test_type = test_type
        self.addr = addr
        self.len = len
        self.val = val
        self.accuracy = accuracy
        self.info = info 
        self.watch_accuracy = watch_accuracy
        self.duration = duration

class SensorDescription(object):
    def __init__(self, model_number, name, firmware, version):
        self.model_number = model_number
        self.name = name
        self.firmware = firmware
        self.version = version
        self.tst = []
        pass

class SensorClassifier(object):
    def __init__(self):
        self.sns = []
        self.sns.append(SensorDescription(MODEL_BALL,    'Ball',     'encrypted_stm8_common_sensors.bin', 2))
        self.sns.append(SensorDescription(MODEL_BUT,     'But',      'encrypted_stm8_common_sensors.bin', 2))
        self.sns.append(SensorDescription(MODEL_ENCODER, 'Encoder',  'encrypted_stm8_common_sensors.bin', 2))
        self.sns.append(SensorDescription(MODEL_LED,     'Led',      'encrypted_stm8_common_sensors.bin', 2))
        self.sns.append(SensorDescription(MODEL_POT,     'Pot',      'encrypted_stm8_common_sensors.bin', 2))
        self.sns.append(SensorDescription(MODEL_RGB,     'RGB',      'encrypted_stm8_common_sensors.bin', 2))
        self.sns.append(SensorDescription(MODEL_MOS,     'MOS',      'encrypted_stm8_common_sensors.bin', 2))
        self.sns.append(SensorDescription(MODEL_ZUMMER,  'Zummer',   'encrypted_stm8_common_sensors.bin', 2)) 
        self.sns.append(SensorDescription(MODEL_NOISE,   'Noise',    'encrypted_stm8_common_sensors.bin', 2))
        self.sns.append(SensorDescription(MODEL_LINE,    'Line',     'encrypted_stm8_common_sensors.bin', 2))
        self.sns.append(SensorDescription(MODEL_USW,     'uSW',      'encrypted_stm8_common_sensors.bin', 2))
        self.sns.append(SensorDescription(MODEL_IR,     'IR',      'encrypted_stm8-ir_rx[BIN].bin', 2))
        self.sns.append(SensorDescription(MODEL_DRIVE1,     'DRIVE1',      'encrypted_drive.bin', 3))
        self.sns.append(SensorDescription(MODEL_DRIVE2,     'DRIVE2',      'encrypted_drive.bin', 3))
        self.sns.append(SensorDescription(MODEL_COLOR,     'Color',      'encrypted_stm8-color[BIN].bin', 2))
        self.sns.append(SensorDescription(MODEL_FORCE,     'Force',      'encrypted_stm8_common_sensors.bin', 3))
        self.sns.append(SensorDescription(MODEL_PRESS,     'Press',      'encrypted_stm8-press.bin', 2))
        self.sns.append(SensorDescription(MODEL_TEMP,     'Temp',      'encrypted_stm8-temp.bin', 2))
        self.sns.append(SensorDescription(MODEL_LIGHT,     'Light',      'encrypted_stm8_common_sensors.bin', 2))
        self.sns.append(SensorDescription(MODEL_MEMS2,     'MEMS2',      'encrypted_stm8-imu-icm20948.bin', 2))
        self.sns.append(SensorDescription(MODEL_AUDIO,     'AUDIO',      'encrypted_stm8-audio.bin', 1))
        self.sns.append(SensorDescription(MODEL_XFACE,     'XFACE',      'encrypted_stm8_xface.bin', 1))
        self.sns.append(SensorDescription(MODEL_XFACE,     'ULTRASONIC',      'encrypted_stm8-ultrasonic.bin', 1))
        self.sns.append(SensorDescription(MODEL_ZIGBEE,    'ZIGBEE',     'encrypted_stm8-zigbrd.bin', 1))
        self.sns.append(SensorDescription(MODEL_AX_S1,    'AX_S1', 0, 1))
        
    def get_by_model_number(self, model_number):
        for x in self.sns:
            if x.model_number == model_number:
                return x
        raise Exception("No such sensor")

    def get_dummy(self, model_number):
        dummy = SensorDescription(model_number, 'Dummy', 'encrypted_stm8_ball.bin', 0)
        dummy.tst.append(SensorRegTest('read8', 0, model_number))
        return dummy

sensor_classifier = SensorClassifier()


class SensorUpdater(object):
    def __init__(self):
        pass

    def update(self, port, file_with_public_key, ser):
        portHandler = PortHandler(port)
        print("UPDATE")
#        lcd.stage('2.Update')
        # Open port
        if portHandler.openPort():
            print('Succeeded to open the port')
#            lcd.info('Succeeded to open the port')
        else:
            print('Failed to open the port')
#            lcd.error('Failed to open the port')
            return -10
        # Set port baudrate
        time.sleep(0.1);
        if portHandler.setBaudRate(BAUDRATE):
            print('Succeeded to change the baudrate') 
#            lcd.info('Succeeded to change the baudrate')
        else:
            print('Failed to change the baudrate')
#            lcd.error('Failed to change the baudrate')        
            return -12

        file_with_public_key = open(file_with_public_key, 'rb')
        public_key = file_with_public_key.read()
        file_with_public_key.close()

        packetHandler = PacketHandler(PROTOCOL_VERSION)

        # reboot
        time.sleep(0.1);
        if portHandler.setBaudRate(57600):
            print('Succeeded to change the baudrate')
#            lcd.info('Succeeded to change the baudrate') 
        else:
            print('Failed to change the baudrate')
#            lcd.error('Failed to change the baudrate')  
            return -14
        packetHandler.write1ByteTxRx(portHandler, 0xFE, 23, 0)
        time.sleep(0.1)

        if portHandler.setBaudRate(BAUDRATE):
            print('Succeeded to change the baudrate')
#            lcd.info('Succeeded to change the baudrate') 
        else:
            print('Failed to change the baudrate')
#            lcd.error('Failed to change the baudrate')  
            return -16
        packetHandler.write1ByteTxRx(portHandler, 0xFE, 23, 0)
        time.sleep(0.1)

        # stop running

        print("Waiting for DXL")
#        lcd.info('Waiting for DXL ...') 
#        lcd.act('Connect 3-Pin DXL->DUT!')
#        lcd.draw_buttons(label_right = ' reset ', color_right = 6, color_left = 0)
        while True:     
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, 0, 0)
            if dxl_comm_result == COMM_SUCCESS:
                print("Sensor found")
#                lcd.info('Sensor found')
                break
#            if lcd.check_buttons():
 #               return -17
 #           lcd.act_blink()

           
        # send the public key
        data = []# list(public_key)
        for i in range(16):
            data.append(struct.unpack('B', public_key[i])[0])

        dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID, 1, len(data), data)
        if dxl_comm_result != COMM_SUCCESS:
            print(dxl_comm_result)
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            return -18
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
            return -20
        else:
            print("Dynamixel has been successfully connected")
#            lcd.info('Dynamixel connected')



        print 'Getting device Model ... ',
        data, dxl_comm_result, dxl_error = packetHandler.readTxRx(portHandler, DXL_ID, 0,  1)
        dynamixel_model = -1
        if dxl_comm_result != COMM_SUCCESS:
            print(dxl_comm_result)
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            return -21
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
            return -21
        else:
            dynamixel_model = data[0]
            print("Dynamixel model is %d" % dynamixel_model)
            #lcd.info('rDynamixel model is ' + bytearray([dynamixel_model]))

        fileName = 'encrypted_stm8_ball.bin'

        try:
            sns = sensor_classifier.get_by_model_number(dynamixel_model)
        except:
            print 'Unknown sensor, use default firmware!'
#            lcd.info('Unknown sensor use default fw')
            sns = sensor_classifier.get_dummy(dynamixel_model)
            pass
            #return -22

        self.model_number = sns.model_number

        fileName = sns.firmware
        print(sns.name),
        print ' ' ,
        print(sns.model_number)
        #fileName = 'encrypted_stm8_ball.bin'

        print 'Firmware ',
        print(fileName)
        input_file = open(fileName, 'rb')
        fileData = input_file.read()
        input_file.close()
        print 'Firmware size ',
        print (len(fileData))
        maxDataSize = 64
        fullPacks = len(fileData) // maxDataSize
        #remainder = len(fileData) % maxDataSize
        offset = 0

        # send the firmware
        if fullPacks > 0:
            for i in range(fullPacks):
                data = [i]
                for j in range(maxDataSize):
                    data.append(struct.unpack('B', fileData[offset])[0])
                    offset += 1
                #print(data)
                dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID, 0, len(data), data)
                if dxl_comm_result != COMM_SUCCESS:
                    print(dxl_comm_result)
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    return -22
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))
                    return -24
                else:
                    #print("Dynamixel has been successfully connected")
                    #print(i)
                    sys.stdout.write('.')
        print 'Succeeded!'
#        lcd.info('Succeeded!')

        time.sleep(0.5)

        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, 2, sns.version)
        if dxl_comm_result != COMM_SUCCESS:
            print(dxl_comm_result)
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            return -24
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
            return -26
        else:
            print("Dynamixel has been successfully connected")
            #lcd.info('Dynamixel connected')

        print 'Reset device'
#        lcd.info('Reset device')  
        packetHandler.write1ByteTxRx(portHandler, DXL_ID, 23, 0)
        time.sleep(0.1)
        portHandler.closePort()

        return 0

    def get_model_number(self):
        return self.model_number

try:
    su = SensorUpdater()
    #while 1:
    #su.update('/dev/ttyACM0', 'public_key.txt')
    time.sleep(0.2)

    time.sleep(3)
    #su.test('/dev/ttyACM0', su.get_model_number())

except KeyboardInterrupt:
    # quit
    sys.exit()
