"""PeekTime class.
"""
#Copyright (c) LiveAction, Inc. 2022. All rights reserved.
#Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
#Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six
import time

from datetime import datetime

from .invariant import TIME_FLAGS_NONE, TIME_FLAGS_NANOSECONDS

# Convert from Ansi time (seconds) to Peek Time (nanoseconds).
ANSI_TIME_MULTIPLIER = 1000000000
# The adjustment in seconds (Ansi Time).
# Seconds between 1/1/1601 and 1/1/1970.
ANSI_TIME_ADJUSTMENT = 11644473600

class PeekTime(object):
    """Peek Time is the number of nanoseconds since
    midnight January 1, 1601.
    
    PeekTime(), with no arguments is set to the current date and time.
    PeekTime(int), uses the integer as the value in nanoseconds.
    PeekTime(string), uses int(string) as the value in nanoseconds.
    PeekTime(PeekTime), copies the value of the other PeekTime.
    """

    value = 0
    """The number of nanoseconds since January 1, 1601."""

    _time_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(self, value=None):
        if value is None:
            self.value = PeekTime.system_time_ns_to_peek_time(time.time_ns())
        elif isinstance(value, int):
            self.value = value if value >= 0 else 0
        elif isinstance(value, six.string_types):
            if len(value) == 30:
                tm = value[0:26] + value[-1]
                dt = datetime.strptime(tm, PeekTime._time_format)
                ms = int(dt.timestamp() * 1000000)
                system_ns = (ms * 1000) + int(value[26:29])
                ns = PeekTime.system_time_ns_to_peek_time(system_ns)
            elif len(value) == 27:
                dt = datetime.strptime(value, PeekTime._time_format)
                ms = int(round(dt.timestamp() * 1000))
                system_ns = (ms * 1000000)
                ns = PeekTime.system_time_ns_to_peek_time(system_ns)
            elif len(value) > 0:
                ns = int(value)
            else:
                ns = 0
            self.value = ns if ns >= 0 else 0
        elif isinstance(value, float):
            ns = PeekTime.system_time_to_peek_time(value)
            self.value = ns if ns >= 0 else 0
        else:
            self.value = 0
            # TODO: Throw a Type Error.

    @classmethod
    def system_time_ns_to_peek_time(cls, value):
        """A Class method that converts a system time_ns to a
        Peek Time value.
        """
        return value + (ANSI_TIME_ADJUSTMENT * ANSI_TIME_MULTIPLIER)

    @classmethod
    def system_time_to_peek_time(cls, value):
        """A Class method that converts a system time to a
        Peek Time value.
        """
        return (value + ANSI_TIME_ADJUSTMENT) * ANSI_TIME_MULTIPLIER

    @classmethod
    def peek_time_to_system_time_ns(cls, value):
        """A Class method that converts a Peek Time value to system
        time_ns.
        """
        return value - (ANSI_TIME_ADJUSTMENT * ANSI_TIME_MULTIPLIER)

    @classmethod
    def peek_time_to_system_time(cls, value):
        """A Class method that converts a Peek Time value to
        system time.
        """
        return int(value / ANSI_TIME_MULTIPLIER) - ANSI_TIME_ADJUSTMENT

    @classmethod
    def _decode_other(cls, other):
        """A Class method that converts various types to an
        integer value.
        """
        if isinstance(other, PeekTime):
            return other.value
        else:
            return int(other)

    def __str__(self):
        return f'{self.value}'

    def __cmp__(self, other):
        return (self.value - PeekTime._decode_other(other))

    # Rich Comparisons - otherwise __cmp__ is called.
    def __lt__(self, other):
        return (self.value < PeekTime._decode_other(other))

    def __le__(self, other):
        return (self.value <= PeekTime._decode_other(other))

    def __eq__(self, other):
        return (self.value == PeekTime._decode_other(other))

    def __ne__(self, other):
        return (self.value != PeekTime._decode_other(other))

    def __gt__(self, other):
        return (self.value > PeekTime._decode_other(other))

    def __ge__(self, other):
        return (self.value >= PeekTime._decode_other(other))

    def __hash__(self):
        return self.value

    def __add__(self, other):
        return PeekTime(self.value + PeekTime._decode_other(other))

    def __sub__(self, other):
        return PeekTime(self.value - PeekTime._decode_other(other))

    def __mul__(self, other):
        return PeekTime(self.value * PeekTime._decode_other(other))

    def from_system_time(self, value):
        """Set the PeekTime from Python System Time, which is the
        number of seconds since January 1, 1970.
        """
        self.value = PeekTime.system_time_to_peek_time(value)

    def time(self):
        """Return the PeekTime as Python System Time, which is
        the number of seconds since January 1, 1970.
        """
        systime = self.value / ANSI_TIME_MULTIPLIER
        if systime > ANSI_TIME_ADJUSTMENT:
            systime -= ANSI_TIME_ADJUSTMENT
        return systime

    def ctime(self):
        """Return the PeekTime as Python
        :class:`ctime <time.ctime>`.
        """
        return time.ctime(self.time())

    def iso_time(self, flags=TIME_FLAGS_NONE):
        """Return the PeekTime as ISO xxxx time format.
        If TIME_FLAG_NANOSECONDS flag is set in flags then extend
        the time to nanoseconds.
        """
        _value = PeekTime.peek_time_to_system_time_ns(self.value)
        flt = _value / ANSI_TIME_MULTIPLIER
        i = int(flt)
        ms = int((flt - i) * 1000000) / 1000000
        dt = datetime.fromtimestamp(i + ms)
        text = dt.isoformat()
        if flags & TIME_FLAGS_NANOSECONDS:
            text += str((self.value % ANSI_TIME_MULTIPLIER) % 1000)
        text += 'Z'
        return text
