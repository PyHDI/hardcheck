from __future__ import absolute_import
from __future__ import print_function
import sys
import os

import convert_by_veriloggen_cpr_ram

# the next line can be removed after installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from veriloggen import *
import hardcheck

expected_verilog = """
module main #
(
  parameter DATA_WIDTH = 32,
  parameter ADDR_WIDTH = 14
)
(
  input CLK,
  input RST,
  input cpr_ctrl_read,
  input cpr_ctrl_write,
  output [32-1:0] cpr_read_fsm,
  output [32-1:0] cpr_read_count,
  output [14-1:0] cpr_read_bram_addr0,
  output [32-1:0] cpr_read_bram_din0,
  output cpr_read_bram_we0,
  output [14-1:0] cpr_read_bram_addr1,
  output [32-1:0] cpr_read_bram_din1,
  output cpr_read_bram_we1,
  input [32-1:0] cpr_write_fsm,
  input [32-1:0] cpr_write_count,
  input [14-1:0] cpr_write_bram_addr0,
  input [32-1:0] cpr_write_bram_din0,
  input cpr_write_bram_we0,
  input [14-1:0] cpr_write_bram_addr1,
  input [32-1:0] cpr_write_bram_din1,
  input cpr_write_bram_we1,
  input [14-1:0] cpr_targ_bram_inst_ext_addr,
  output [32-1:0] cpr_targ_bram_inst_ext_rdata,
  input [32-1:0] cpr_targ_bram_inst_ext_wdata,
  input cpr_targ_bram_inst_ext_wvalid
);

  reg [14-1:0] bram_addr0;
  reg [32-1:0] bram_din0;
  reg bram_we0;
  wire [32-1:0] bram_dout0;
  reg [14-1:0] bram_addr1;
  reg [32-1:0] bram_din1;
  reg bram_we1;
  wire [32-1:0] bram_dout1;

  cpr_ram_2
  #(
    .DATA_WIDTH(32),
    .ADDR_WIDTH(14)
  )
  bram_inst
  (
    .CLK(CLK),
    .ADDR0(bram_addr0),
    .DIN0(bram_din0),
    .WE0(bram_we0),
    .DOUT0(bram_dout0),
    .ADDR1(bram_addr1),
    .DIN1(bram_din1),
    .WE1(bram_we1),
    .DOUT1(bram_dout1),
    .cpr_ctrl_read(cpr_ctrl_read),
    .cpr_ctrl_write(cpr_ctrl_write),
    .ext_addr(cpr_targ_bram_inst_ext_addr),
    .ext_rdata(cpr_targ_bram_inst_ext_rdata),
    .ext_wdata(cpr_targ_bram_inst_ext_wdata),
    .ext_wvalid(cpr_targ_bram_inst_ext_wvalid)
  );

  reg [32-1:0] fsm;
  localparam fsm_init = 0;
  reg [32-1:0] count;
  localparam fsm_1 = 1;
  localparam fsm_2 = 2;

  always @(posedge CLK) begin
    if(RST) begin
      fsm <= 0;
      count <= 0;
    end else if(cpr_ctrl_write) begin
      fsm <= cpr_write_fsm;
      count <= cpr_write_count;
      bram_addr0 <= cpr_write_bram_addr0;
      bram_din0 <= cpr_write_bram_din0;
      bram_we0 <= cpr_write_bram_we0;
      bram_addr1 <= cpr_write_bram_addr1;
      bram_din1 <= cpr_write_bram_din1;
      bram_we1 <= cpr_write_bram_we1;
    end else if(!cpr_ctrl_read) begin
      case(fsm)
        0: begin
          bram_addr0 <= 0;
          bram_din0 <= 0;
          bram_we0 <= 0;
          bram_addr1 <= 0;
          bram_din1 <= 0;
          bram_we1 <= 0;
          fsm <= 1;
        end
        1: begin
          bram_addr0 <= count + 0;
          bram_din0 <= count;
          bram_we0 <= 1;
          count <= count + 1;
          bram_addr1 <= count + 64;
          bram_din1 <= count;
          bram_we1 <= 1;
          count <= count + 1;
          if(count == 63) begin
            fsm <= 2;
          end 
        end
      endcase
    end 
  end

  assign cpr_read_fsm = fsm;
  assign cpr_read_count = count;
  assign cpr_read_bram_addr0 = bram_addr0;
  assign cpr_read_bram_din0 = bram_din0;
  assign cpr_read_bram_we0 = bram_we0;
  assign cpr_read_bram_addr1 = bram_addr1;
  assign cpr_read_bram_din1 = bram_din1;
  assign cpr_read_bram_we1 = bram_we1;

endmodule



module cpr_ram_2 #
(
  parameter DATA_WIDTH = 32,
  parameter ADDR_WIDTH = 14
)
(
  input CLK,
  input [14-1:0] ADDR0,
  input [32-1:0] DIN0,
  input WE0,
  output [32-1:0] DOUT0,
  input [14-1:0] ADDR1,
  input [32-1:0] DIN1,
  input WE1,
  output [32-1:0] DOUT1,
  input cpr_ctrl_read,
  input cpr_ctrl_write,
  input [14-1:0] ext_addr,
  input [32-1:0] ext_wdata,
  input ext_wvalid,
  output [32-1:0] ext_rdata
);

  reg [14-1:0] delay_ADDR0;
  reg [14-1:0] delay_ADDR1;
  reg [14-1:0] ext_daddr;
  reg [32-1:0] mem [0:16384-1];

  always @(posedge CLK) begin
    if(WE0) begin
      mem[ADDR0] <= DIN0;
    end 
    delay_ADDR0 <= ADDR0;
  end

  assign DOUT0 = mem[delay_ADDR0];

  always @(posedge CLK) begin
    if(WE1) begin
      mem[ADDR1] <= DIN1;
    end 
    delay_ADDR1 <= ADDR1;
  end

  assign DOUT1 = mem[delay_ADDR1];

  always @(posedge CLK) begin
    if(ext_wvalid) begin
      mem[ext_addr] <= ext_wdata;
    end 
    delay_ADDR1 <= ext_addr;
  end

  assign ext_rdata = mem[ext_daddr];

endmodule
"""

def test():
    orig = convert_by_veriloggen_cpr_ram.mkMain()
    conv = hardcheck.convert(orig)
    code = conv.to_verilog()

    from pyverilog.vparser.parser import VerilogParser
    from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
    parser = VerilogParser()
    expected_ast = parser.parse(expected_verilog)
    codegen = ASTCodeGenerator()
    expected_code = codegen.visit(expected_ast)

    assert(expected_code == code)
