__version__ = '0.1.2'

import serial
from pynput.keyboard import Key, Controller
import pyautogui as pag

pag.FAILSAFE = False

keyboard = Controller()
def begin(port):
  ser = serial.Serial(port, 115200)
  
  print(ser.name)         # check which port was really used
  
  
  while True:
  	line = ser.readline().decode('UTF-8')
  	if 'Lst' in line:
  		drag = 1
  		continue
  	elif 'Rst' in line:
  		drag = 2
  		continue
  	elif 'Stop' in line:
  		drag = 0
  		continue
  
  	if 'left' in line:
  		pag.click(clicks = int(line.split()[1]))
  	elif 'right' in line:
  		pag.click(button = 'right', clicks = int(line.split()[1]))
  	elif drag == 1:
  		pos = line.split()
  		pos[0] = int(pos[0])
  		pos[1] = int(pos[1])
  		pag.drag(pos[0], pos[1], 0, button = 'left')
  	elif drag == 2:
  		pos = line.split()
  		pos[0] = int(pos[0])
  		pos[1] = int(pos[1])
  		pag.drag(pos[0], pos[1], 0, button = 'left')
  	else:
  		pos = line.split()
  		pos[0] = int(pos[0])
  		pos[1] = int(pos[1])
  		pag.moveRel(pos[0], pos[1], 0)
  		continue
  

ser.close()