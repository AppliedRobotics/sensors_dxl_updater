import serial
import os
import sys
import time
import threading
#import test_lcd
from subprocess import STDOUT, check_output
from update_firmware import SensorUpdater

ON = True
OFF = False


def set_led(port, val):
	if val:
		port.write(b'1\b')
	else:
		port.write(b'0\b')

def blink_led(port, n, repeats = 1):
	for i in range(repeats):
		for j in range(9):
			set_led(port, 1)
			time.sleep(0.035)
			set_led(port, 0)
			time.sleep(0.035)
		time.sleep(1)

		for j in range(n):
			set_led(port, 1)
			time.sleep(0.300)
			set_led(port, 0)
			time.sleep(0.300)
		time.sleep(2)

def wait_resstart_blinking_led(port, blink_n):
	port.write(b"\x15\xAA")  #enable touch screen scan
	lcd_draw_buttons(port)
	while port.readline().find('2'): #< 0 and port.readline().find('start') < 0:
		pass
		#blink_led(port, blink_n)
	#while 1:
  	#	print(port.readline())

class SensorDxlUpdate(object):
	def __init__(self):
		self.is_first = True
		pass

	def run(self):
		os.system('../rs485  /dev/ttyS2  1')
		ser = serial.Serial('/dev/ttyS1', 115200, timeout=1)
#		lcd = test_lcd.Lcd(ser)
		set_led(ser, 1)
		#lcd.beeptest()
#		lcd.beep(ON)
		print ('start')

		#su = SensorUpdater()
		#su.test('/dev/ttyACM0', 0x15, ser, lcd)

		set_led(ser, 0)

		su = SensorUpdater()

		su.update('/dev/ttyS2', 'public_key.txt', ser)

    #su.update('/dev/ttyACM0', 'public_key.txt', ser, lcd)
#		try:
#			if su.update('/dev/ttyS2', 'public_key.txt', ser) < 0:
#				print 'Error: can\'t update firmware'
#				lcd.dialog('Error: can\'t update firmware', right_btn = ' RESET ', beep = True)
#				return
#		except:
#			print 'Error: can\'t update firmware with exception'
#			lcd.dialog('Error: can\'t update firmware with exception', right_btn = ' RESET ', beep = True)
#			return

		print('Firmware updated!')
#		lcd.info('Firmware updated!') 
		time.sleep(2.5)

		set_led(ser, 1)
#		lcd.info('Test Complete!', txt_clr = 10) 
#		lcd.beep_n(4)
#		time.sleep(2.5)

#		print 'waiting restart ... '
#		lcd.info('waiting restart ...')

sdt = SensorDxlUpdate()
sdt.run()
time.sleep(0.2)
sys.exit()
