
import os

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
from _thread import start_new_thread

def prepare_buf(data_source, buf):
    for n in range(int(DAC_BUF_SIZE/2)):
            global index1
            buf.append(data_source[index1])
            buf.append(128)
            index1 += 1
            if index1 == len(data_source):
                index1 = 0  

# Control table address
ADDR_DAC_ENABLE            = 29
ADDR_MODE_SELECT           = 28
ADDR_STATUS_A              = 35
ADDR_STATUS_B              = 36
ADDR_BUF_A                 = 26
ADDR_BUF_B                 = 27   

# Protocol version
PROTOCOL_VERSION            = 1.0               # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                      = 161                 # Dynamixel ID : 1
BAUDRATE                    = 1000000             # Dynamixel default baudrate : 1000000
DEVICENAME                  = 'COM31'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

DAC_ENABLE               = 2                 # Value for enabling the dac
DAC_DISABLE              = 1                 # Value for disabling the dac
MODE_DAC                 = 32
DAC_BUF_SIZE             = 70

#channel1 = [144, 159, 174, 189, 202, 214, 225, 234, 242, 248, 252, 254, 254, 252, 248, 242, 234, 225, 214, 202, 189, 174, 159, 144, 128, 112, 97, 82, 67, 54, 42, 31, 22, 14, 8, 4, 2, 2, 4, 8, 14, 22, 31, 42, 54, 67, 82, 97, 112, 128]
channel1 = [202, 248, 248, 202, 128, 54, 8, 8, 54, 128]
#channel1 = [132, 136, 140, 144, 148, 152, 155, 159, 163, 167, 171, 174, 178, 182, 185, 189, 192, 196, 199, 202, 205, 208, 211, 214, 217, 220, 223, 225, 228, 230, 232, 234, 236, 238, 240, 242, 244, 245, 247, 248, 249, 250, 251, 252, 252, 253, 253, 254, 254, 254, 254, 254, 253, 253, 252, 252, 251, 250, 249, 248, 247, 245, 244, 242, 240, 238, 236, 234, 232, 230, 228, 225, 223, 220, 217, 214, 211, 208, 205, 202, 199, 196, 192, 189, 185, 182, 178, 174, 171, 167, 163, 159, 155, 152, 148, 144, 140, 136, 132, 128, 124, 120, 116, 112, 108, 104, 101, 97, 93, 89, 85, 82, 78, 74, 71, 67, 64, 60, 57, 54, 51, 48, 45, 42, 39, 36, 33, 31, 28, 26, 24, 22, 20, 18, 16, 14, 12, 11, 9, 8, 7, 6, 5, 4, 4, 3, 3, 2, 2, 2, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 31, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 64, 67, 71, 74, 78, 82, 85, 89, 93, 97, 101, 104, 108, 112, 116, 120, 124, 128, ]
index = 0

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

# Enable Dynamixel Torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MODE_SELECT, MODE_DAC)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("Mode selected")

dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_DAC_ENABLE, DAC_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("DAC enabled")

index1 = 0
index2 = 0
mixed_buf = []
dac_status = 0
now = datetime.datetime.now()
startpoint = now.minute*100+now.second



while 1:
    now = datetime.datetime.now()
    if now.minute*100+now.second - startpoint > 15:
        print("ESC")
        break
    dac_status, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, DXL_ID, ADDR_STATUS_A)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    
    portHandler.setPacketTimeoutMillis(100)
    if dac_status == 1:   #0xAA
        prepare_buf(channel1, mixed_buf)
        dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID, ADDR_BUF_A, DAC_BUF_SIZE, mixed_buf)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        mixed_buf = []

    if dac_status == 2:  #0xBB
        prepare_buf(channel1, mixed_buf)
        dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID, ADDR_BUF_B, DAC_BUF_SIZE, mixed_buf)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        mixed_buf = []
    
    if dac_status == 3:  #0xBB
        prepare_buf(channel1, mixed_buf)
        dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID, ADDR_BUF_A, DAC_BUF_SIZE, mixed_buf)
        prepare_buf(channel1, mixed_buf)
        dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID, ADDR_BUF_B, DAC_BUF_SIZE, mixed_buf)
        mixed_buf = []

dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_DAC_ENABLE, DAC_DISABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("DAC disabled")    
# Close port
portHandler.closePort()

