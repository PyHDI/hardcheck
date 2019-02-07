from __future__ import absolute_import
from __future__ import print_function
import sys
import os
import math

# the next line can be removed after installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from veriloggen import *
import hardcheck

def mkCprRam(datawidth=32, addrwidth=10, numports=2):
    m = Module('cpr_ram_%d' % numports)

    datawidth = m.Parameter('DATA_WIDTH', datawidth)
    addrwidth = m.Parameter('ADDR_WIDTH', addrwidth)

    clk = m.Input('CLK')
    ports = []
    for i in range(numports):
        addr = m.Input('ADDR%d' % i, addrwidth)
        din = m.Input('DIN%d' % i, datawidth)
        we = m.Input('WE%d' % i)
        dout = m.Output('DOUT%d' % i, datawidth)
        delay_addr = m.Reg('delay_ADDR%d' % i, addrwidth)
        ports.append( (addr, din, we, dout, delay_addr) )

    # CPR ports
    ctrl_read = m.Input('cpr_ctrl_read')
    ctrl_write = m.Input('cpr_ctrl_write')
    
    eaddr = m.Input('ext_addr', addrwidth)
    edin = m.Input('ext_wdata', datawidth)
    ewe = m.Input('ext_wvalid')
    edout = m.Output('ext_rdata', datawidth)
    edelay_addr = m.Reg('ext_daddr', addrwidth)
        
    mem = m.Reg('mem', datawidth, length=Int(2)**addrwidth)

    # main port
    for i in range(numports):
        addr, din ,we, dout, delay_addr = ports[i]
        m.Always(Posedge(clk))(
            If(we)(
                mem[addr](din)
            ),
            delay_addr(addr)
        )
        m.Assign(dout(mem[delay_addr]))

    # CPR port
    m.Always(Posedge(clk))(
        If(ewe)(
            mem[eaddr](edin)
        ),
        delay_addr(eaddr)
    )
    m.Assign(edout(mem[edelay_addr]))

    return m

def mkMain(n=128, datawidth=32, numports=2):
    m = Module('main')

    clk = m.Input('CLK')
    rst = m.Input('RST')

    addrwidth = int(math.log(n, 2)) * 2

    datawidth = m.Parameter('DATA_WIDTH', datawidth)
    addrwidth = m.Parameter('ADDR_WIDTH', addrwidth)
    
    bram = mkCprRam(datawidth, addrwidth, numports)

    bram_ports = []
    for i in range(numports):
        addr = m.Reg('bram_addr%d' % i, addrwidth)
        din = m.Reg('bram_din%d' % i, datawidth)
        we = m.Reg('bram_we%d' % i)
        dout = m.Wire('bram_dout%d' % i, datawidth)
        bram_ports.append( [addr, din, we, dout] )

    params = [ (datawidth.name, datawidth), 
               (addrwidth.name, addrwidth) ]
    ports = [ clk ]
    for bram_port in bram_ports:
        ports.extend(bram_port)

    # BRAM instance
    m.Instance(bram, 'bram_inst', params=params, ports=ports)

    # example how to access BRAM
    fsm = FSM(m, 'fsm', clk, rst)
    
    for addr, din, we, dout in bram_ports:
        fsm.add( addr(0), din(0), we(0) )

    fsm.goto_next()

    count = m.Reg('count', 32, initval=0)
    for port, (addr, din, we, dout) in enumerate(bram_ports):
        fsm.add( addr(count+port*n//numports), din(count), we(1), count.inc() )

    fsm.goto_next(cond=count==n//numports-1)
    
    fsm.make_always()
    
    return m

if __name__ == '__main__':
    orig = mkMain()
    #orig_verilog = orig.to_verilog()
    #print(orig_verilog)
    
    conv = hardcheck.convert(orig)
    conv_verilog = conv.to_verilog()
    print(conv_verilog)
