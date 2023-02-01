
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


#get music values from file
file_path = "C:/Users/infer/Documents/stm8-xface/Desktop/Sound/Eagles_py.txt"
f = open(file_path, "r")
content = f.read()
f.close()
#remove extra symbols and split into array on delimiters
content.replace("\n", "")
content.replace("\\n", "")
spl = content.split(",")
blocks = []
block = []
#split music into blocks sized like buffer that we send
#samples go 1 by 1 for two channels
#second channel is just 128 all the time for test
for i in range(len(spl)):
    block.append(int(str(spl[i]), 16))
    block.append(128)
    if len(block) == DAC_BUF_SIZE:
        blocks.append(block)
        block = []

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

# Select mode - DAC
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MODE_SELECT, MODE_DAC)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("Mode selected")
#Enable DAC
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_DAC_ENABLE, DAC_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("DAC enabled")
#represents number of buffer where to write data
dac_status = 0
#counter for switching to the next block each time
blocks_cnt = 0


while 1:
    #read buffer status
    if blocks_cnt == len(blocks):
        break
    dac_status, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, DXL_ID, ADDR_STATUS_A)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    
    portHandler.setPacketTimeoutMillis(100)
    #if buffer 1 is finished and ready to receive new values - write to buf 1 
    if dac_status == 1:   
        dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID, ADDR_BUF_A, DAC_BUF_SIZE, blocks[blocks_cnt])
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        blocks_cnt += 1
    #if buffer 2 is finished and ready to receive new values - write to buf 2 
    if dac_status == 2:  
        dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID, ADDR_BUF_B, DAC_BUF_SIZE, blocks[blocks_cnt])
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        blocks_cnt += 1
    #Used in the beginning to write both buffers
    if dac_status == 3:  
        dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID, ADDR_BUF_A, DAC_BUF_SIZE, blocks[blocks_cnt])
        
        dxl_comm_result, dxl_error = packetHandler.writeTxRx(portHandler, DXL_ID, ADDR_BUF_B, DAC_BUF_SIZE, blocks[blocks_cnt])
        blocks_cnt += 2
        
#when test finished switch off the DAC
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_DAC_ENABLE, DAC_DISABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("DAC disabled")    
# Close port
portHandler.closePort()


