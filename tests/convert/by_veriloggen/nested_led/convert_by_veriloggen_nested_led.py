from __future__ import absolute_import
from __future__ import print_function
import sys
import os

# the next line can be removed after installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from veriloggen import *
import hardcheck

def mkLed():
    m = Module('blinkled')

    subled = mkSubLed()
    ports = m.copy_ports(subled)
    params = m.copy_params(subled)
    clk = ports['CLK']
    rst = ports['RST']
    led = ports['LED']
    inv_led = m.OutputRegLike(led, name='INV_LED')

    m.Always(Posedge(clk))(
        If(rst)(
            inv_led(0)
        ).Else(
            inv_led(Unot(led))
        )
    )

    m.Instance(subled, 'inst_subled',
               params=m.connect_params(subled),
               ports=m.connect_ports(subled))

    return m

def mkSubLed():
    m = Module('sub_blinkled')
    width = m.Parameter('WIDTH', 8)
    clk = m.Input('CLK')
    rst = m.Input('RST')
    led = m.OutputReg('LED', width)
    count = m.Reg('count', 32)

    m.Always(Posedge(clk))(
        If(rst)(
            count(0)
        ).Else(
            If(count == 1023)(
                count(0)
            ).Else(
                count(count + 1)
            )
        ))
    
    m.Always(Posedge(clk))(
        If(rst)(
            led(0)
        ).Else(
            If(count == 1024 - 1)(
                led(led + 1)
            )
        ))
    
    return m

if __name__ == '__main__':
    orig = mkLed()
    #orig_verilog = orig.to_verilog()
    #print(orig_verilog)

    conv = hardcheck.convert(orig)
    conv_verilog = conv.to_verilog()
    print(conv_verilog)
