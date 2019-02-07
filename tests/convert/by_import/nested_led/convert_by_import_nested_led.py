from __future__ import absolute_import
from __future__ import print_function
import sys
import os

# the next line can be removed after installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from veriloggen import *
import veriloggen.resolver.resolver as resolver
import hardcheck

if __name__ == '__main__':
    filename = os.path.dirname(os.path.abspath(__file__)) + '/nested_led.v'
    conv = hardcheck.convert_from_file('blinkled', filename)
    conv_verilog = conv.to_verilog()
    print(conv_verilog)
