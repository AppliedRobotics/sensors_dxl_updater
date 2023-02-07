
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
import keyboard
from wave_generator import WaveGenerator
from threading import Timer

def prepare_buf(data_source_1, data_source_2, buf):
    for n in range(int(DAC_BUF_SIZE/2)):
            global index1
            global index2
            buf.append(data_source_1[index1])
            buf.append(data_source_2[index2])
            index1 += 1
            index2 += 1
            if index1 == len(data_source_1):
                index1 = 0  
            if index2 == len(data_source_2):
                index2 = 0  

# Control table address
ADDR_MODE_SELECT            = 28

# Protocol version
PROTOCOL_VERSION            = 1.0               # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                      = 161               # Dynamixel ID : 1
BAUDRATE                    = 1000000           # Dynamixel default baudrate : 1000000
DEVICENAME                  = '/dev/ttyS2'           # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

MODE_DAC                = 32                   # Value to enable DAC 
DAC_BUF_SIZE            = 120
                                                #Statuses for transmitting audio
BUF_A_READY             = 250                  #Buffer A is ready to be written
BUF_B_READY             = 251                  #Buffer B is ready to be written
BOTH_READY              = 252                  #Both buffers are ready to be written

index = 0

channel1 = WaveGenerator.generate_sine(20, 120) # Generate sine for dac, first arg is number of samples and second is amplitude
channel2 = WaveGenerator.generate_sine(20, 120)

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

portHandler.setPacketTimeoutMillis(0)                           #Set serial timeout to 0
dacPH = DACPacketHandler()                                      #Create handler for serial communication    
index1 = 0
index2 = 0
mixed_buf = []

status = [0]

try:
    os.system('../rs485 /dev/ttyS2 1')
    while 1:
        status = dacPH.rxPacket(portHandler)                        #Read status
        if status == [BUF_A_READY]:                                         #250 = 0xFA, write to 1st buffer
            prepare_buf(channel1, channel2, mixed_buf)    
            dacPH.txPacket(portHandler, 250, mixed_buf)
            mixed_buf = []
        if status == [BUF_B_READY]:                                         #251 = 0xFB, write to 2nd buffer
            prepare_buf(channel1, channel2, mixed_buf)
            dacPH.txPacket(portHandler, 251, mixed_buf)
            mixed_buf = []    
        if status == [BOTH_READY]:                                         #252 = 0xFC, write to both buffers
            prepare_buf(channel1, channel2, mixed_buf)
            dacPH.txPacket(portHandler, 250, mixed_buf)
            mixed_buf = []
        
            prepare_buf(channel1, channel2, mixed_buf)
            dacPH.txPacket(portHandler, 251, mixed_buf)
            mixed_buf = []
except KeyboardInterrupt:
    dacPH.return_to_DXL(portHandler)                                #Return to dxl mode and switch off the dac 
    time.sleep(0.5) 
    # Close port
    portHandler.closePort()
    print("")
    print("Port closed")
    exit()
