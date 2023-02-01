
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
import keyboard



# Control table address

ADDR_BUF_A                 = 26  
ADDR_DAC_ENABLE            = 29
ADDR_MODE_SELECT           = 28

# Protocol version
PROTOCOL_VERSION            = 1.0               # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                      = 161                 # Dynamixel ID : 1
BAUDRATE                    = 1000000             # Dynamixel default baudrate : 1000000
DEVICENAME                  = 'COM49'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"


DAC_BUF_SIZE             = 20
DAC_ENABLE               = 2                 # Value for enabling the dac
DAC_DISABLE              = 1                 # Value for disabling the dac
MODE_DAC                 = 33

ENA1 = 1
DIS1 = 2
ENA2 = 16
DIS2 = 32
ENA_BOTH = 17
DIS_BOTH = 33

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
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

parameters = [7, 100, 8, 100]
# Select mode - DAC
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MODE_SELECT, MODE_DAC)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("Mode selected")

dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID, ADDR_BUF_A, 4, parameters)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("Parameters set")

# Select mode - DAC
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, 24, 2)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("PWM1 enabled")
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, 25, 2)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("PWM1 enabled")



while 1:
    if keyboard.is_pressed('ESC'):                              #if ESC pressed, stop translation and return to dxl mode
        break



dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, 24, 1)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("PWM disabled")
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, 25, 1)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("PWM disabled")

  
# Close port
portHandler.closePort()

