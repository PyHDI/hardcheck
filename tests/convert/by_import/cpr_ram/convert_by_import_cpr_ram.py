from __future__ import absolute_import
from __future__ import print_function
import sys
import os

# the next line can be removed after installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from veriloggen import *
import hardcheck

if __name__ == '__main__':
    filename = os.path.dirname(os.path.abspath(__file__)) + '/cpr_ram.v'
    conv = hardcheck.convert_from_file('main', filename)
    conv_verilog = conv.to_verilog()
    print(conv_verilog)
