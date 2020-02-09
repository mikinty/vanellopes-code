'''
Button API to control and detect button presses.
'''

from time import sleep
import signal
import sys
from random import randint

# Hardware packages
import board
import busio
from digitalio import Direction, Pull
from RPi import GPIO
from adafruit_mcp230xx.mcp23017 import MCP23017

from CONST import *

GPIO.cleanup()

# Start I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Instantiate GPIO expander
mcp = MCP23017(i2c, address=MCP_ADDR_BUTTON_0)

print('running setup')
# Instantiate all the pins
pins = []
for pin in range(0, MCP_NUM_PINS):
    currPin = mcp.get_pin(pin)

    if pin in MCP_INPUT_PINS:
        print('{0} set as input'.format(pin))
        currPin.direction = Direction.INPUT
        currPin.pull = Pull.UP
    else:
        print('{0} set as output'.format(pin))
        currPin.direction = Direction.OUTPUT

    pins.append(currPin)

# TODO: assign pins
# Set up interrupts
mcp.interrupt_enable = 0x0300

# NOTE: When I try to set bits to 1 for comparison they don't work...
mcp.interrupt_configuration = 0x0000

# Enable open-drain pull-down, active low, also OR INTA INTB
# See the adafruit library notes for more details on thie code
mcp.io_control = 0x44
mcp.clear_ints()

# On interrupt, check all buttons that are pressed
def interrupt_handler(port):
    pressed_buttons = []
    for pin in MCP_INPUT_PINS:
        currPin = pins[pin]

        # Button pressed if its value is 0
        if not currPin.value:
            pressed_buttons.append(pin)

    # We are ready to accept the next set of presses
    mcp.clear_ints()

    # print('Pressed {}'.format(pressed_buttons))

    # TODO: need to figure out a way to pair the assignment
    # of buttons and their LED pins
    # PROBABLY can just make a button_class and have
    # two fields, the LED pin and the INPUT pin
    pressed_buttons = [x - 8 for x in pressed_buttons]
    handle_presses(pressed_buttons)

# Set up the interrupt handler
GPIO.setmode(GPIO.BCM)
GPIO.setup(RPI_INTERRUPT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect (
    RPI_INTERRUPT_PIN,
    GPIO.FALLING,
    callback=interrupt_handler,
    bouncetime=20
)

### SIGNAL HANDLING ###
def signal_handler(sig, frame):
    print('Exiting game...')

    # Cleanup pins on the Raspberry Pi
    GPIO.cleanup()

    # Quit program
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

### INTERFACE FOR HARDWARE ###
def turn_on(pin):
    pins[pin].value = True

def turn_off(pin):
    pins[pin].value = False

### GAME LOGIC STATE ###
is_lit = [0 for x in range(NUM_BUTTONS)]
points = 0


### GAME HELPER FUNCTIONS ###
def handle_presses(buttons):
    global points
    global is_lit

    oldPoints = points
    for b in buttons:
        if is_lit[b]:
            points += 1

            is_lit[b] = 0
            turn_off(b)

    # TODO: send this score over to the scoreboard
    # Even if score doesn't change, you should send
    # to the scoreboard

    if points != oldPoints:
        print('Score: {0}'.format(points))

### MAIN GAME LOGIC ###
def main():
    # Main game logic
    try:
        while True:
            # Generating buttons to turn on
            sleep(0.5)
            goal = randint(0, NUM_BUTTONS - 1)

            # print(goal)

            is_lit[goal] = 1
            turn_on(goal)
    finally:
        # Cleanup pins on the Raspberry Pi
        GPIO.cleanup()
main()
