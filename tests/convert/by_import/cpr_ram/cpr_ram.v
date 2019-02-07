module main #
(
  parameter DATA_WIDTH = 32,
  parameter ADDR_WIDTH = 14
)
(
  input CLK,
  input RST
);

  reg [ADDR_WIDTH-1:0] bram_addr0;
  reg [DATA_WIDTH-1:0] bram_din0;
  reg bram_we0;
  wire [DATA_WIDTH-1:0] bram_dout0;
  reg [ADDR_WIDTH-1:0] bram_addr1;
  reg [DATA_WIDTH-1:0] bram_din1;
  reg bram_we1;
  wire [DATA_WIDTH-1:0] bram_dout1;

  cpr_ram_2
  #(
    .DATA_WIDTH(DATA_WIDTH),
    .ADDR_WIDTH(ADDR_WIDTH)
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
    .DOUT1(bram_dout1)
  );

  reg [32-1:0] fsm;
  localparam fsm_init = 0;
  reg [32-1:0] count;
  localparam fsm_1 = 1;
  localparam fsm_2 = 2;

  always @(posedge CLK) begin
    if(RST) begin
      fsm <= fsm_init;
      count <= 0;
    end else begin
      case(fsm)
        fsm_init: begin
          bram_addr0 <= 0;
          bram_din0 <= 0;
          bram_we0 <= 0;
          bram_addr1 <= 0;
          bram_din1 <= 0;
          bram_we1 <= 0;
          fsm <= fsm_1;
        end
        fsm_1: begin
          bram_addr0 <= count + 0;
          bram_din0 <= count;
          bram_we0 <= 1;
          count <= count + 1;
          bram_addr1 <= count + 64;
          bram_din1 <= count;
          bram_we1 <= 1;
          count <= count + 1;
          if(count == 63) begin
            fsm <= fsm_2;
          end 
        end
      endcase
    end
  end


endmodule



module cpr_ram_2 #
(
  parameter DATA_WIDTH = 32,
  parameter ADDR_WIDTH = 14
)
(
  input CLK,
  input [ADDR_WIDTH-1:0] ADDR0,
  input [DATA_WIDTH-1:0] DIN0,
  input WE0,
  output [DATA_WIDTH-1:0] DOUT0,
  input [ADDR_WIDTH-1:0] ADDR1,
  input [DATA_WIDTH-1:0] DIN1,
  input WE1,
  output [DATA_WIDTH-1:0] DOUT1,
  input cpr_ctrl_read,
  input cpr_ctrl_write,
  input [ADDR_WIDTH-1:0] ext_addr,
  input [DATA_WIDTH-1:0] ext_wdata,
  input ext_wvalid,
  output [DATA_WIDTH-1:0] ext_rdata
);

  reg [ADDR_WIDTH-1:0] delay_ADDR0;
  reg [ADDR_WIDTH-1:0] delay_ADDR1;
  reg [ADDR_WIDTH-1:0] ext_daddr;
  reg [DATA_WIDTH-1:0] mem [0:2**ADDR_WIDTH-1];

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


