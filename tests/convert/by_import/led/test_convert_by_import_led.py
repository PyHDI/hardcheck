from __future__ import absolute_import
from __future__ import print_function
import sys
import os

import convert_by_import_led

# the next line can be removed after installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from veriloggen import *
import hardcheck

expected_verilog = """
module blinkled #
(
  parameter WIDTH = 8
)
(
  input CLK,
  input RST,
  output reg [8-1:0] LED,
  input cpr_ctrl_read,
  input cpr_ctrl_write,
  output [32-1:0] cpr_read_count,
  output [8-1:0] cpr_read_LED,
  input [32-1:0] cpr_write_count,
  input [8-1:0] cpr_write_LED
);

  reg [32-1:0] count;

  always @(posedge CLK) begin
    if(RST) begin
      count <= 0;
    end else if(cpr_ctrl_write) begin
      count <= cpr_write_count;
    end else if(!cpr_ctrl_read) begin
      if(count == 1023) begin
        count <= 0;
      end else begin
        count <= count + 1;
      end
    end 
  end


  always @(posedge CLK) begin
    if(RST) begin
      LED <= 0;
    end else if(cpr_ctrl_write) begin
      LED <= cpr_write_LED;
    end else if(!cpr_ctrl_read) begin
      if(count == 1023) begin
        LED <= LED + 1;
      end 
    end 
  end

  assign cpr_read_count = count;
  assign cpr_read_LED = LED;

endmodule
"""


def test():
    filename = os.path.dirname(os.path.abspath(__file__)) + '/led.v'
    conv = hardcheck.convert_from_file('blinkled', filename)
    code = conv.to_verilog()

    from pyverilog.vparser.parser import VerilogParser
    from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
    parser = VerilogParser()
    expected_ast = parser.parse(expected_verilog)
    codegen = ASTCodeGenerator()
    expected_code = codegen.visit(expected_ast)

    assert(expected_code == code)
