import rtmidi
import time
import csv
import numpy as np

FILTER_CUTOFF = 43

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

# start midi
midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

port_number = None
for i, port in enumerate(available_ports):
    print(port)
    # minilogue midi IN port
    # minilogue:minilogue minilogue _ SOUND 28:1
    if 'SOUND' in port:
        port_number = i
        break

if port_number is not None:
    midiout.open_port(port_number)
    print("connecting to:", port)
else:
    print('Could not find the synthesizer.')
    exit(1)

def normalize_to_range(value, value_min, value_max, range_min, range_max):
    if value_max == value_min:
        return range_min
    return ((value - value_min) / (value_max - value_min)) * (range_max - range_min) + range_min


print('playing program...')
# sets filter to 0
with open('Cordyceps militari.txt', 'r') as file:
    reader = csv.reader(file, delimiter='\t')
    next(reader)  # Skip the header row

    data = [row[1] for row in reader]
    data = list(map(float, data))

    for i in range(len(data)):
        if i < 95000:
            continue
        # Find the min and max of the last 1000 samples (or fewer if less than 1000 samples have been read)
        window = data[max(0, i - 1000):i+1]
        min_value, max_value = min(window), max(window)

        # Normalize the current sample
        value = data[i]
        normalized_value = normalize_to_range(value, min_value, max_value, 30, 127)

        cc_value = round(normalized_value)  # convert to integer for MIDI CC
        midiout.send_message([0xB0, FILTER_CUTOFF, cc_value])
        print("current value:", cc_value, value)
        time.sleep(0.2)

del midiout
