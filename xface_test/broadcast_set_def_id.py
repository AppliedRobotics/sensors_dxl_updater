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

BAUDRATE = 1000000
BROADCAST_ID = 0xFE
ADDR_DEV_ID = 3
DXL_ID = 161

DEVICENAME = '/dev/ttyS2'
PROTOCOL_VERSION = 1.0

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

def broadcast_set_def_id():
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, BROADCAST_ID, ADDR_DEV_ID, DXL_ID)
    if dxl_comm_result == COMM_SUCCESS:
        print("Set default ID")
        
try:
    port_open()
    broadcast_set_def_id()
except KeyboardInterrupt:
    time.sleep(0.5)

portHandler.closePort()
quit()