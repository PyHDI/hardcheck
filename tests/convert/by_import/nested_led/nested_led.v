module blinkled #
(
  parameter WIDTH = 8
)
(
  input CLK,
  input RST,
  output [WIDTH-1:0] LED,
  output reg [WIDTH-1:0] INV_LED
);


  always @(posedge CLK) begin
    if(RST) begin
      INV_LED <= 0;
    end else begin
      INV_LED <= ~LED;
    end
  end


  sub_blinkled
  #(
    .WIDTH(WIDTH)
  )
  inst_subled
  (
    .CLK(CLK),
    .RST(RST),
    .LED(LED)
  );


endmodule



module sub_blinkled #
(
  parameter WIDTH = 8
)
(
  input CLK,
  input RST,
  output reg [WIDTH-1:0] LED
);

  reg [32-1:0] count;

  always @(posedge CLK) begin
    if(RST) begin
      count <= 0;
    end else begin
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
    end else begin
      if(count == 1023) begin
        LED <= LED + 1;
      end 
    end
  end


endmodule
