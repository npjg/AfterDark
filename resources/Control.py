
import self_documenting_struct as struct
from enum import Enum

class ControlType(Enum):
    CTL_NONE = 0
    CTL_STRSLIDER = 1
    CTL_NUMSLIDER = 2
    CTL_COMBOBOX = 3
    CTL_BUTTON = 4
    CTL_CHECKBOX = 5

## 'Reserved' fields should be nulls, but older modules have grunge
## in these bytes and so the engine generally ignores them.
class Control:
    def __init__(self, stream, resource_declaration, resource_library):
        self.control_type = ControlType(struct.unpack.uint16_le(stream))
        self.title = None
        if self.control_type == ControlType.CTL_NONE:
            # A null control is just 32 total null bytes 
            # (2 bytes for the type and 30 unused bytes)
            stream.read(30)
            return
        
        # The spec specifies a 15-character string followed by a 0,
        # but it makes more sense to view this as a null-terminated string.
        # with the rest of the space filled by 0s.
        self.title = stream.read(0x0f).rstrip(b'\x00').decode('latin-1')
        if self.control_type == ControlType.CTL_STRSLIDER:
            self.control = StringSlider(stream)
        elif self.control_type == ControlType.CTL_NUMSLIDER:
            self.control = NumericSlider(stream)
        elif self.control_type == ControlType.CTL_COMBOBOX:
            self.control = ComboBox(stream)
        elif self.control_type == ControlType.CTL_BUTTON:
            self.control = CommandButton(stream)
        elif self.control_type == ControlType.CTL_CHECKBOX:
            self.control = CheckBox(stream)

## Sliders have a 'position' on the control panel which is resolved into
## one of 101 possible results, which you can think of as having the values
## of 0 through 100. 
##
## As the user moves the slider, two things happen: one, a string to be
## displayed is selected, and two, a return value is selected.  For reasons
## of compatibility with some older modules, the ADW3.0 engine will never
## return a value other than 0 or one of the explicitly defined slider
## values.  (But you can have up to 100 of these, so you can get back any
## value you may want in your own modules.)
##
## The string to be displayed is selected by comparing the actual slider
## position (resolved to a range of 0 to 100) against the table of slider
## values.  The first bound value which is not greater-than-or-equal-to
## the actual value is what will determine the string selection.
##
## The value to be returned is the *previous* 'nBound' value to that which
## determined the string selection.  Since 0 is always assumed as a valid
## boundary value, it can be returned as well.
##
## Thus, if the slider string array has elements "First" and "Second" and the
## bounds array has elements 10 and 20, the following actual slider positions
## will have the indicated results:
##
## Actual    String Shown     Value returned
##   0           First              0
##   1           First              0
##   5           First              0
##   9           First              0
##  10          Second             10
##  11          Second             10
##  15          Second             10
##  19          Second             10
##
## etc.  In this example, if there were only these two elements then all
## further slider positions would also return 10 and display 'Second'.
class StringSlider:
    def __init__(self, stream):
        # READ THE HEADER.
        self.reserved1 = stream.read(5)
        string_count = struct.unpack.uint16_le(stream)
        self.slider_start_position = struct.unpack.uint16_le(stream)
        self.reserved2 = stream.read(6)

        # READ THE SLIDER STRINGS.
        self.slider_strings = []
        for index in range(string_count):
            slider_string = stream.read(0x10).rstrip(b'\x00').decode('latin-1')
            self.slider_strings.append(slider_string)

        # READ THE SLIDER BOUNDS.
        self.slider_bounds = []
        for index in range(string_count):
            slider_bound = struct.unpack.uint16_le(stream)
            assert slider_bound <= 100

            self.slider_bounds.append(slider_bound)

## The other type of slider: a 'numeric' one. Modules don't bother using these
## very much, as you can get all the same effects by using a string slider
## and appropriate logic in the module. 
##
## There are some wrinkles similar to the notes for the string sliders but 
## rather more complex. Don't get too clever.
class NumericSlider:
    # The string can be provided before or after the number.
    # If there is no string, this should be NONE.
    class StringPosition(Enum):
        NONE = 0
        PREFIX = 1
        SUFFIX = 2

    def __init__(self, stream):
        self.reserved1 = stream.read(5)
        self.slider_start_position = struct.unpack.uint16_le(stream)
        self.reserved2 = stream.read(6)
        self.prefix_suffix_string = stream.read(0x06).rstrip(b'\x00').decode('latin-1')
        self.reserved3 = stream.read(10)
        self.slider_lower_bound = struct.unpack.uint16_le(stream)
        self.slider_upper_bound = struct.unpack.uint16_le(stream)
        self.discrete_slider_positions = struct.unpack.uint16_le(stream)
        self.string_position = self.StringPosition(struct.unpack.uint16_le(stream))

# TODO: Does the index start at 1 or 0?
class ComboBox:
    def __init__(self, stream):
        self.reserved1 = stream.read(5)

        string_count = struct.unpack.uint16_le(stream)
        self.start_index = struct.unpack.uint16_le(stream)
        self.reserved2 = stream.read(6)

        self.strings = []
        for index in range(string_count):
            string = stream.read(0x10).rstrip(b'\x00').decode('latin-1')
            self.strings.append(string)

## A command button used to trigger a dialog.
class CommandButton:
    def __init__(self, stream):
        self.reserved = stream.read(0x0f)

class CheckBox:
    def __init__(self, stream):
        self.reserved1 = stream.read(7)
        self.initially_checked = (struct.unpack.uint16_le(stream) == 1)
        self.reserved2 = stream.read(6)
