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

# Control table address

ADDR_BUF_A                  = 26
ADDR_MODE_SELECT            = 28
ADDR_CH1_EN                 = 24
ADDR_CH2_EN                 = 25

# Protocol version
PROTOCOL_VERSION            = 1.0               # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                      = 161                 # Dynamixel ID : 1
BAUDRATE                    = 1000000             # Dynamixel default baudrate : 1000000
DEVICENAME                  = '/dev/ttyS2'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

MODE_PWM                 = 33

PWM1_DIV                = 8
PWM2_DIV                = 8
PWM1_DUTY_CYCLE         = 50
PWM2_DUTY_CYCLE         = 240


ENA1 = 1
DIS1 = 2
ENA2 = 16
DIS2 = 32
ENA_BOTH = 17
DIS_BOTH = 33

portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

try:
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

    parameters = [PWM1_DIV, PWM1_DUTY_CYCLE, PWM2_DIV, PWM2_DUTY_CYCLE]
    # Select mode - DAC
    
    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS: 
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MODE_SELECT, MODE_PWM)

    print("Mode selected")

    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID, ADDR_BUF_A, len(parameters), parameters)

    print("Parameters set")

    # Select mode - DAC
    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_CH1_EN, 2)

    print("PWM1 enabled")
    
    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_CH2_EN, 2)

    print("PWM2 enabled")

    while True:
        pass

except KeyboardInterrupt:
    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_CH1_EN, 1)

    print("")
    print("PWM1 disabled")

    dxl_comm_result = 1
    while dxl_comm_result != COMM_SUCCESS:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_CH2_EN, 1)

    print("PWM2 disabled")

      
    # Close port
    portHandler.closePort()
    print ("Port closed")

