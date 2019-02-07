from __future__ import absolute_import
from __future__ import print_function
import sys
import os

import convert_by_veriloggen_nested_led

# the next line can be removed after installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

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
  output [8-1:0] LED,
  output reg [8-1:0] INV_LED,
  input cpr_ctrl_read,
  input cpr_ctrl_write,
  output [8-1:0] cpr_read_INV_LED,
  input [8-1:0] cpr_write_INV_LED,
  output [32-1:0] cpr_read_inst_subled_count,
  output [8-1:0] cpr_read_inst_subled_LED,
  output [32-1:0] cpr_write_inst_subled_count,
  output [8-1:0] cpr_write_inst_subled_LED
);


  always @(posedge CLK) begin
    if(RST) begin
      INV_LED <= 0;
    end else if(cpr_ctrl_write) begin
      INV_LED <= cpr_write_INV_LED;
    end else if(!cpr_ctrl_read) begin
      INV_LED <= ~LED;
    end 
  end


  sub_blinkled
  #(
    .WIDTH(8)
  )
  inst_subled
  (
    .CLK(CLK),
    .RST(RST),
    .LED(LED),
    .cpr_ctrl_read(cpr_ctrl_read),
    .cpr_ctrl_write(cpr_ctrl_write),
    .cpr_read_count(cpr_read_inst_subled_count),
    .cpr_read_LED(cpr_read_inst_subled_LED),
    .cpr_write_count(cpr_write_inst_subled_count),
    .cpr_write_LED(cpr_write_inst_subled_LED)
  );

  assign cpr_read_INV_LED = INV_LED;

endmodule



module sub_blinkled #
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
    orig = convert_by_veriloggen_nested_led.mkLed()
    conv = hardcheck.convert(orig)
    code = conv.to_verilog()

    from pyverilog.vparser.parser import VerilogParser
    from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
    parser = VerilogParser()
    expected_ast = parser.parse(expected_verilog)
    codegen = ASTCodeGenerator()
    expected_code = codegen.visit(expected_ast)

    assert(expected_code == code)
