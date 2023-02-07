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


############################ USER SCRIPT SETTINGS ###############################
#################################################################################
                                                                                #
USART_SETTINGS    = 0b10010000          #SET SETTINGS (use XFace manual)        #
DEVICE_NUMBER     = 3                   #SET NUMBER OF DEVICES (MIN 1)          #
txbuf             = [0x01, 0x02, 0x03]  #SET TX BUFFER (any available length)   #
                                                                                #            
#################################################################################


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

txrx_result = 0
SUCCESS = 1

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

    print("")
    time.sleep(1)

############################ USART SETTINGS ##########################


def usart_set(master_id, slave_id):

    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, master_id , ADDR_MODE_SELECT, MODE_UART_USARTM)

    print("Mode selected for DEVICE", (master_id - DXL_ID), "with ID", master_id)

    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        if(USART_SETTINGS & 0b10000000):
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, slave_id , ADDR_MODE_SELECT, MODE_USART_SLAVE)
        else:
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, slave_id , ADDR_MODE_SELECT, MODE_UART_USARTM)
    
    print("Mode selected for DEVICE", (slave_id - DXL_ID), "with ID", slave_id)
    
    time.sleep(0.5)

    for id in master_id, slave_id:
        dxl_comm_result = 1
        while dxl_comm_result != COMM_SUCCESS:
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_SETTINGS, USART_SETTINGS)
        
        print("Settings installed for DEVICE", (master_id-DXL_ID), "with ID", id)

    time.sleep(0.5)

    print("")

###################### USART TRANSMIT (DEVICE 1) ########################

def usart_send(master_id, slave_id):

    for id in master_id, slave_id:
        dxl_comm_result = 1
        while dxl_comm_result != COMM_SUCCESS:
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_DATA_LENGTH, len(txbuf))
            
        print("Length set for DEVICE", (id - DXL_ID), "with ID", id)
    
    print ("")

    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, master_id, ADDR_BUF_A, len(txbuf), txbuf)
    
    print("TX buffer set for DEVICE 1:", txbuf, "with ID", master_id)
    print("")
    
    for id in slave_id, master_id:
        dxl_comm_result = 1
        while dxl_comm_result != COMM_SUCCESS:
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_USART_ENABLE, 2)
    
    print("Start transmitting")
    print("")
    time.sleep(0.5)

###################### USART READ (DEVICE 2 ... n) ##########################

def  usart_read(slave_id):
    rxbuf = []
    global txrx_result
    
    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        rxbuf, dxl_comm_result, dxl_error = packetHandler.readTxRx(portHandler, slave_id, ADDR_BUF_A, len(txbuf))

    print("RX buffer of DEVICE", (slave_id - DXL_ID), "with ID", slave_id, ":", rxbuf)
    print("")

    if rxbuf == txbuf:
        txrx_result = SUCCESS
        print("Successful transmit")
    else:
        txrx_result = 0
        print("Unsuccessful transmit")
        print("Trying again...")
    
    print("")
    time.sleep(0.2)

def usart_ring_txrx():
    dev_id = DXL_ID
    global txrx_result

    while dev_id < DXL_ID+DEVICE_NUMBER:
        dev_id += 1

        master_id = dev_id
        if(master_id == DXL_ID+DEVICE_NUMBER):
            slave_id = DXL_ID+1
        else:
            slave_id = master_id+1

        print("")
        print("ROUND", (dev_id-DXL_ID))
        print("Master ID:", master_id)
        print("Slave ID:", slave_id)

        usart_set(master_id, slave_id)
        while txrx_result != SUCCESS:
            usart_send(master_id, slave_id)
            usart_read(slave_id)
            time.sleep(1)
        txrx_result = 0

try:
    port_open()
    show_info()
    id_set()
    usart_ring_txrx()
    set_def_id()
#    usart_set(self, )
except KeyboardInterrupt:
    time.sleep(0.5)

portHandler.closePort()
quit()