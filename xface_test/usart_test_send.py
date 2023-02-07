
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
ADDR_BUF_A                 = 26
ADDR_USART_ENABLE          = 29
ADDR_MODE_SELECT           = 28
ADDR_DATA_LENGTH           = 25
# Protocol version
PROTOCOL_VERSION            = 1.0               # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                      = 161                 # Dynamixel ID : 1
BAUDRATE                    = 1000000             # Dynamixel default baudrate : 1000000
DEVICENAME                  = '/dev/ttyS2'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"


USART_BUF_SIZE                = 64
USART_WRITE                   = 2                 # Value for enabling the dac
USART_READ                    = 1                 # Value for disabling the dac
MODE_USART                    = 36


SETTINGS = 34


portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)


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

dxl_comm_result = 1
while dxl_comm_result != COMM_SUCCESS:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MODE_SELECT, MODE_USART)

print("Mode selected")

time.sleep(0.5)

dxl_comm_result = 1
while dxl_comm_result != COMM_SUCCESS:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, SETTINGS, 0b10001000)

print("Settings installed")

time.sleep(0.5)

buf = [1, 2, 3]

dxl_comm_result = 1
while dxl_comm_result != COMM_SUCCESS:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_DATA_LENGTH, len(buf))

print("Length sent")

dxl_comm_result = 1
while dxl_comm_result != COMM_SUCCESS:
    dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID, ADDR_BUF_A, len(buf), buf)

print("buf sent")

dxl_comm_result = 1
while dxl_comm_result != COMM_SUCCESS:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_USART_ENABLE, 2)

print("Write buffer")

# Close port
portHandler.closePort()

