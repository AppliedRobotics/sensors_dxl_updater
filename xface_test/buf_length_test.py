
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


# Control table address
ADDR_STATUS_A              = 35
ADDR_STATUS_B              = 36
ADDR_BUF_A                 = 26
ADDR_BUF_B                 = 27   
ADDR_DAC_ENABLE            = 29
ADDR_MODE_SELECT           = 28

# Protocol version
PROTOCOL_VERSION            = 1.0               # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                      = 161                 # Dynamixel ID : 1
BAUDRATE                    = 1000000             # Dynamixel default baudrate : 1000000
DEVICENAME                  = 'COM31'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"


DAC_BUF_SIZE             = 20
DAC_ENABLE               = 2                 # Value for enabling the dac
DAC_DISABLE              = 1                 # Value for disabling the dac
MODE_DAC                 = 32

portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)


# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port baudrate
if portHandler.setBaudRate(57600):
    print("Succeeded to change the baudrate to 57600")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

a, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, 161, 0)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print(a)
# Set port baudrate
if portHandler.setBaudRate(1000000):
    print("Succeeded to change the baudrate to 1000000")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

a, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, 161, 0)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print(a)

  
# Close port
portHandler.closePort()

