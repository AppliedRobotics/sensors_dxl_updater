
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
import time
from dac_packet_handler import DACPacketHandler


def prepare_buf(data_source, buf):
    for n in range(int(DAC_BUF_SIZE/2)):
            global index1
            buf.append(data_source[index1])
            buf.append(128)
            index1 += 1
            if index1 == len(data_source):
                index1 = 0  

# Control table address
ADDR_MODE_SELECT           = 28  

# Protocol version
PROTOCOL_VERSION            = 1.0           # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                      = 161           # Dynamixel ID : 1
BAUDRATE                    = 1000000       # Dynamixel default baudrate : 1000000
DEVICENAME                  = 'COM31'       # Check which port is being used on your controller
                                            # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

MODE_DAC                 = 32                #Value for dxl register to enable dac mode
DAC_BUF_SIZE             = 120               #Size of one dac data buffer. Don't change without corresponding changes in MCU


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

# Enable Dynamixel DAC
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MODE_SELECT, MODE_DAC)

if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("Mode selected")

dacPH = DACPacketHandler()
blocks_cnt = 0
status = [0]

while 1:
    if blocks_cnt == len(blocks):                                       #Detect the end of the song to stop translation 
        break                                                           #and switch off dac
    status = dacPH.rxPacket(portHandler)                                #Get MCU status 
    if(status == [250] or status == [251]):                             #Status = 0xFA or 0xFB refer to dac buffers A and B
        dacPH.txPacket(portHandler, status[0], blocks[blocks_cnt])      #Write next block of the song to dac
        blocks_cnt += 1
    if(status == [252]):                                                #status = 0xFC, initial state - write to both buffers

        dacPH.txPacket(portHandler, 250, blocks[blocks_cnt])            #The same thing but for 2 buffers
        print(blocks[blocks_cnt])
        blocks_cnt += 1
        dacPH.txPacket(portHandler, 251, blocks[blocks_cnt])
        print(blocks[blocks_cnt])
        blocks_cnt += 1

 

dacPH.return_to_DXL(portHandler)                                        #Send command to return to dxl protocol mode
time.sleep(0.3)                                                         #Important! It takes some time for MCU to switch to DXL
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_DAC_ENABLE, DAC_DISABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("DAC disabled")    
# Close port
portHandler.closePort()

