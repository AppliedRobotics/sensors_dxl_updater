import struct
import os
from socket import timeout

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *                    # Uses Dynamixel SDK library
import datetime

# DXL settings

PROTOCOL_VERSION            = 1.0               # See which protocol version is used in the Dynamixel
BROADCAST_ID                = 0xFE
DXL_ID                      = 161                 # Dynamixel ID : 1
BAUDRATE                    = 1000000             # Dynamixel default baudrate : 1000000
DEVICENAME                  = '/dev/ttyS2'    # Check which port is being used on your controller

# XFACE registers map

ADDR_DEV_ID                 = 3
ADDR_SETTINGS               = 34
ADDR_MODE_SELECT            = 28
ADDR_DATA_LENGTH            = 25
ADDR_BUF_A                  = 26
ADDR_USART_ENABLE           = 29
ADDR_STATUS_A               = 35

# XFACE settings

MODE_USART                  = 36
USART_SETTINGS              = 0b00010000

# Script settings

DEVICE_NUMBER               = 2
txbuf                       = [0x01, 0x02, 0x03]

portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)


def port_open():
    # Open port
    os.system('../rs485  /dev/ttyS2  1')
    if portHandler.openPort():
        print("Succeeded to open the port")
    else:
        print("Failed to open the port")
        print("Press any key to terminate...")
        getch()
        quit()

    # Set port baudrate
    if portHandler.setBaudRate(BAUDRATE):
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
        print("Press any key to terminate...")
        getch()
        quit()
    print("")

####################### SET DEFAULT IDs ##############################
def set_def_id():
    out_flag = 0
    while True:
        dev_id = DXL_ID
        while dev_id < (DXL_ID+DEVICE_NUMBER):
            dev_id += 1
            
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dev_id, 0, 0)
            if dxl_comm_result == COMM_SUCCESS:
                print("DEVICE", (dev_id-DXL_ID), "found")
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dev_id, ADDR_DEV_ID, DXL_ID)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))
                else:
                    print("Set default ID:", DXL_ID, "for DEVICE", (dev_id-DXL_ID))
                    out_flag += 1
                    break
        if out_flag == DEVICE_NUMBER:
            break
    #dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, BROADCAST_ID, ADDR_DEV_ID, DXL_ID)
    print("Disconnect devices")
    print("")

###################### SET DIFFERENT IDs #############################
def id_set():
    dev_id = DXL_ID
    while dev_id < (DXL_ID+DEVICE_NUMBER):
        print("Connect DEVICE", (dev_id-DXL_ID+1))
        while True: 
            dev_id += 1

            dxl_comm_result = 1
            while dxl_comm_result != COMM_SUCCESS:
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, 0, 0)

            print("DEVICE", (dev_id-DXL_ID), "found")
            
            dxl_comm_result = 1
            while dxl_comm_result != COMM_SUCCESS:
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_DEV_ID, dev_id)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))
                    
            print("Set ID:", (dev_id), "for DEVICE", (dev_id-DXL_ID))
            break

        time.sleep(1)
    print("")

############################ USART SETTINGS ##########################


def usart_set():
    dev_id = DXL_ID
    while dev_id < DXL_ID + DEVICE_NUMBER:
        dev_id += 1
        

        dxl_comm_result = 1
        while dxl_comm_result != COMM_SUCCESS:
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dev_id, ADDR_MODE_SELECT, MODE_USART)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            if dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))
    
        print("Mode selected for DEVICE", (dev_id-DXL_ID))
        
        time.sleep(0.5)

        dxl_comm_result = 1
        while dxl_comm_result != COMM_SUCCESS:
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dev_id, ADDR_SETTINGS, USART_SETTINGS)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))
        
        print("Settings installed for DEVICE", (dev_id-DXL_ID))

        time.sleep(1)

    print("")

###################### USART TRANSMIT (DEVICE 1) ########################

def usart_send():
    dev_id = DXL_ID
    while dev_id < (DXL_ID + DEVICE_NUMBER):
        dev_id += 1
        
        dxl_comm_result = 1
        while dxl_comm_result != COMM_SUCCESS:
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dev_id, ADDR_DATA_LENGTH, len(txbuf))
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))
            
        print("Length set for DEVICE", (dev_id-DXL_ID))

    print ("")

    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID + 1, ADDR_BUF_A, len(txbuf), txbuf)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
    
    print("TX buffer set for DEVICE 1:", txbuf)

    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, BROADCAST_ID, ADDR_USART_ENABLE, 2)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
    
    print("")
    print("Start transmitting")
    print("")
    time.sleep(0.5)

###################### USART READ (DEVICE 2 ... n) ##########################

def  usart_read():
    rxbuf = []
    dev_id = DXL_ID+1
    while dev_id < DXL_ID+DEVICE_NUMBER:
        dev_id += 1
        bytes_count = 0
        while bytes_count < len(txbuf):
            rxbuf.append(packetHandler.read1ByteTxRx(portHandler, 163, (ADDR_BUF_A + bytes_count))[0])
#            rxbuf.pop()
#            rxbuf.pop()
            bytes_count += 1
        print("RX buffer of DEVICE", dev_id - DXL_ID, ":", rxbuf)

    if rxbuf == txbuf:
        print("Successful transmit")
    else:
        print("Unsuccessful transmit")
    print("")
    time.sleep(0.5)

try:
    port_open()
    id_set()
    usart_set()
    usart_send()
    usart_read()
    set_def_id()
#    usart_set(self, )
except KeyboardInterrupt:
    time.sleep(0.5)

portHandler.closePort()
quit()