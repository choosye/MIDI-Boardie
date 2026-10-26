```python
import keypad
import touchio
from adafruit_midi.control_change import ControlChange
from microcontroller import pin

from kmk.keys import KC
from kmk.kmk_keyboard import KMKKeyboard
from kmk.modules.encoder import EncoderHandler
from kmk.modules.midi import MidiKeys
from kmk.modules.potentiometer import PotentiometerHandler
from kmk.scanners import Scanner
from kmk.scanners.keypad import KeysScanner


# Custom scanner for capacitive touch pads
# Do not touch pads while the board boots!
class TouchScanner(Scanner):
    def __init__(self, pins):
        self.pads = [touchio.TouchIn(p) for p in pins]
        self.pressed = [False] * len(pins)

    @property
    def key_count(self):
        return len(self.pads)

    def scan_for_changes(self):
        for i, pad in enumerate(self.pads):
            touched = pad.value
            if touched != self.pressed[i]:
                self.pressed[i] = touched
                return keypad.Event(i + self.offset, touched)


# Create the keyboard and MIDI handler
keyboard = KMKKeyboard()
midi = MidiKeys()


# Define the controls
keyboard.matrix = [
    # Seven capacitive touch pads
    TouchScanner([
        pin.GPIO13,
        pin.GPIO12,
        pin.GPIO11,
        pin.GPIO10,
        pin.GPIO9,
        pin.GPIO8,
        pin.GPIO7,
    ]),

    # Three physical switches
    KeysScanner(
        [pin.GPIO4, pin.GPIO5, pin.GPIO6],
        value_when_pressed=False,
        pull=True,
    ),
]


# Assign MIDI notes to the controls
# Touch pads: C major scale
# Switches: kick, snare, hi-hat
keyboard.keymap = [[
    KC.MIDI_NOTE(60),
    KC.MIDI_NOTE(62),
    KC.MIDI_NOTE(64),
    KC.MIDI_NOTE(65),
    KC.MIDI_NOTE(67),
    KC.MIDI_NOTE(69),
    KC.MIDI_NOTE(71),

    KC.MIDI_NOTE(36),
    KC.MIDI_NOTE(38),
    KC.MIDI_NOTE(42),
]]


# Rotary encoder: computer volume
encoder = EncoderHandler()
encoder.pins = (
    (pin.GPIO43, pin.GPIO44, None),
)
encoder.map = [
    ((KC.VOLD, KC.VOLU, KC.NO),)
]


# Two sliders: MIDI control changes
# Slider 1: CC 1 (modulation)
# Slider 2: CC 7 (channel volume)
sliders = PotentiometerHandler()
sliders.pins = (
    (
        pin.GPIO2,
        lambda state: midi.send(
            ControlChange(1, state.position)
        ),
    ),
    (
        pin.GPIO1,
        lambda state: midi.send(
            ControlChange(7, state.position)
        ),
    ),
)


# Enable MIDI, encoder and sliders
keyboard.modules = [
    midi,
    encoder,
    sliders,
]


# Start the controller
if __name__ == '__main__':
    keyboard.go()
```
