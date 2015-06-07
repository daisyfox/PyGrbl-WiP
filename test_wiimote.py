# shebang:  PYTHON 2.7

import cwiid, time

button_delay = 0.1 # debounce

print 'Please press buttons 1 + 2 on your Wiimote now ...'
time.sleep(1)

# This code attempts to connect to your Wiimote and if it fails the program quits
try:
  wii=cwiid.Wiimote("CC:9E:00:CD:96:FC")
except RuntimeError:
  print "Cannot connect to your Wiimote. Run again and make sure you are holding buttons 1 + 2!"
  quit()

print 'Wiimote connection established!\n'

time.sleep(1)

wii.rpt_mode = cwiid.RPT_BTN
wii.led = 1

while True:

  buttons = wii.state['buttons']

  # Detects whether + and - are held down and if they are it quits the program
  if (buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0):
    print '\nClosing connection ...'
    # NOTE: This is how you RUMBLE the Wiimote
    wii.rumble = 1
    time.sleep(0.25)
    wii.rumble = 0
    wii.close()
    #exit(wii)

  # The following code detects whether any of the Wiimotes buttons have been pressed and then prints a statement to the screen!
  if (buttons - cwiid.BTN_LEFT == 0):
    #print 'Left pressed'
    print('Jog X-')
    time.sleep(button_delay)

  if(buttons - cwiid.BTN_RIGHT == 0):
    #print 'Right pressed'
    print('Jog X+')
    time.sleep(button_delay)

  if (buttons - cwiid.BTN_UP == 0):
    #print 'Up pressed'
    print('Jog Y+')
    time.sleep(button_delay)

  if (buttons - cwiid.BTN_DOWN == 0):
    #print 'Down pressed'
    print('Jog Y-')
    time.sleep(button_delay)

  if (buttons  - (cwiid.BTN_B + cwiid.BTN_UP) == 0):
    print('Jog Z+')
    time.sleep(button_delay)

  if (buttons - (cwiid.BTN_B + cwiid.BTN_DOWN) == 0):
    print('Jog Z-')
    time.sleep(button_delay)

  if (buttons - cwiid.BTN_1 == 0):
    print 'Button 1 pressed'
    time.sleep(button_delay)

  if (buttons - cwiid.BTN_2 == 0):
    print 'Button 2 pressed'
    time.sleep(button_delay)

  if (buttons - cwiid.BTN_A == 0):
    print 'Button A pressed'
    time.sleep(button_delay)

##  if (buttons & cwiid.BTN_B):
##    print 'Button B pressed'
##    time.sleep(button_delay)
##
  if (buttons & cwiid.BTN_HOME):
    wii.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC
    check = 0
    while check == 0:
      print(wii.state['acc'])
      time.sleep(0.01)
      check = (buttons & cwiid.BTN_HOME)
    time.sleep(button_delay)

  if (buttons & cwiid.BTN_MINUS):
    print 'Minus Button pressed'
    time.sleep(button_delay)

  if (buttons & cwiid.BTN_PLUS):
    print 'Plus Button pressed'
    time.sleep(button_delay)
