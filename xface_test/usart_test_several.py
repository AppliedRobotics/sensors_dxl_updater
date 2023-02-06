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

MODE_UART_USARTM            = 36
MODE_USART_SLAVE            = 37
USART_SETTINGS              = 0b10010000

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

####################### SHOW INFO ####################################

def show_info():
    print("INTERFACE SETTINGS:")
    print("")
    print("Number of devices:", DEVICE_NUMBER)

    print ("")
    if(USART_SETTINGS & 0b10000000):
        print ("MODE: USART")
        print("CPOL =", (USART_SETTINGS & 0b00000001))
        print("CPHA =", ((USART_SETTINGS & 0b00000010)>>1))
    else:
        print ("MODE: UART")
    
    print ("")
    print("BAUDRATE:")

    if    (USART_SETTINGS & 0b00001000):
        print ("9600")
    elif  (USART_SETTINGS & 0b00010000):
        print ("19200")
    elif ((USART_SETTINGS & 0b00011000) == 0b00011000):
        print ("57600")
    elif  (USART_SETTINGS & 0b00100000):
        print ("115200")
    elif ((USART_SETTINGS & 0b00101000) == 0b00101000):
        print ("200000")
    elif ((USART_SETTINGS & 0b00110000) == 0b00110000):
        print ("250000")
    elif ((USART_SETTINGS & 0b00111000) == 0b00111000):
        print ("400000")
    elif  (USART_SETTINGS & 0b01000000):
        print ("500000")
    elif ((USART_SETTINGS & 0b01001000) == 0b01001000):
        print ("1000000")

    print ("")
    print ("WORD LENGTH:")
    
    if(USART_SETTINGS & 0b00000100):
        print ("9 BIT")
    else:
        print ("8 BIT")

    print ("")

####################### SET DEFAULT IDs ##############################
def set_def_id():

    dev_id = DXL_ID
    while dev_id < (DXL_ID+DEVICE_NUMBER):
        dev_id += 1
        
        dxl_comm_result = 1
        while dxl_comm_result != COMM_SUCCESS:
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dev_id, 0, 0)

        print("DEVICE", (dev_id-DXL_ID), "found")
            
        dxl_comm_result = 1
        while dxl_comm_result != COMM_SUCCESS:
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dev_id, ADDR_DEV_ID, DXL_ID)

        print("Set default ID:", DXL_ID, "for DEVICE", (dev_id-DXL_ID))
    
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
                
            print("Set ID:", (dev_id), "for DEVICE", (dev_id-DXL_ID))
            break

        time.sleep(1)
    print("")

############################ USART SETTINGS ##########################


def usart_set():

    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID+1 , ADDR_MODE_SELECT, MODE_UART_USARTM)

    dev_id = DXL_ID
    dev_id += 1
    while dev_id < DXL_ID + DEVICE_NUMBER:
        dev_id += 1
        dxl_comm_result = 1
        while dxl_comm_result != COMM_SUCCESS:
            if(USART_SETTINGS & 0b10000000):
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dev_id , ADDR_MODE_SELECT, MODE_USART_SLAVE)
            else:
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dev_id , ADDR_MODE_SELECT, MODE_UART_USARTM)
    
        print("Mode selected for DEVICE", (dev_id-DXL_ID))
    
    time.sleep(0.5)

    dev_id = DXL_ID
    while dev_id < DXL_ID + DEVICE_NUMBER:
        dev_id += 1

        dxl_comm_result = 1
        while dxl_comm_result != COMM_SUCCESS:
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dev_id, ADDR_SETTINGS, USART_SETTINGS)
        
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
            
        print("Length set for DEVICE", (dev_id-DXL_ID))

    print ("")

    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID + 1, ADDR_BUF_A, len(txbuf), txbuf)
    
    print("TX buffer set for DEVICE 1:", txbuf)

    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, BROADCAST_ID, ADDR_USART_ENABLE, 2)
    
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
        dxl_comm_result = 1
        while dxl_comm_result != COMM_SUCCESS:
            rxbuf, dxl_comm_result, dxl_error = packetHandler.readTxRx(portHandler, dev_id, ADDR_BUF_A, len(txbuf))

        print("RX buffer of DEVICE", dev_id - DXL_ID, ":", rxbuf)

    if rxbuf == txbuf:
        print("Successful transmit")
    else:
        print("Unsuccessful transmit")
    print("")
    time.sleep(0.5)

try:
    port_open()
    show_info()
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