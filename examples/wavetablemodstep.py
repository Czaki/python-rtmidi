#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# wavetablemodstep.py
#
"""Play a note and step through MIDI Control Change #0 (modulation) values.

Optionally allows to send a Control Change #70 first, to set the wavetable
of the current sound on a Waldorf Microwave II/XT(k) synthesizer.

I use this with a Microwave sound program where the CC #0 is mapped to
wavetable position of osscillator 1. This script then allows me to listen to
all the waves in a selected wavetable in succession.

"""

import time
import rtmidi


class Midi(object):
    """Encapsulate MIDI output."""

    def __init__(self, port):
        self.midi = rtmidi.MidiOut()
        self.midi.open_port(port)

    def play_stepping(self, note, dur=0.2, step=1, vel=64, rvel=None, ch=0):
        """Play given note and step through cc #0 values over time."""
        # note on
        self.midi.send_message([0x90 | (ch & 0xF), note & 0x7F, vel & 0x7F])

        # step through modulation controller values
        for i in xrange(0, 128, step):
            self.midi.send_message([0xB0 | (ch & 0xF), 1, i])
            time.sleep(dur)

        # note off
        self.midi.send_message([0x80 | (ch & 0xF), note & 0x7F,
            (rvel if rvel is not None else vel) & 0x7F])

    def reset_controllers(self, ch=0):
        """Reset controllers on given channel."""
        self.midi.send_message([0xB0 | (ch & 0xF), 121, 0])

    def set_wavetable(self, wt, ch=0):
        """Set wavetable for current sound to given number."""
        self.midi.send_message([0xB0 | (ch & 0xF), 70, wt & 0x7F])

    def close(self):
        """Close MIDI outpurt."""
        self.midi.close_port()
        del self.midi


if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-c', '--channel', type=int, default=0,
        help="MIDI channel (1-based, default: %(default)s)")
    argparser.add_argument('-d', '--device', type=int, default=0,
        help="MIDI output device (default: %(default)s)")
    argparser.add_argument('-l', '--length', type=float, default=0.3,
        help="Length (in sec.) of each wave (default: %(default)s)")
    argparser.add_argument('-n', '--note', type=int, default=60,
        help="MIDI note number to play (default: %(default)s)")
    argparser.add_argument('-w', '--wavetable', type=int,
        help="Set wavetable number (1-based, default: do not set)")

    args = argparser.parse_args()

    m = Midi(args.device)

    if args.wavetable:
        m.set_wavetable(args.wavetable-1, ch=args.channel-1)
        time.sleep(0.1)

    m.reset_controllers(ch=args.channel-1)
    m.play_stepping(args.note, dur=args.length, step=2, ch=args.channel-1)
    m.reset_controllers(ch=args.channel-1)
    m.close()
