module Cxu0 (
  input               cmd_valid,
  output              cmd_ready,
  input      [2:0]    cmd_payload_function_id,
  input      [31:0]   cmd_payload_inputs_0,
  input      [31:0]   cmd_payload_inputs_1,
  input      [2:0]    cmd_payload_state_id,
  input      [3:0]    cmd_payload_cxu_id,
  input               cmd_payload_ready,
  output              rsp_valid,
  input               rsp_ready,
  output     [31:0]   rsp_payload_outputs_0,
  output              rsp_payload_ready,
  input               clk,
  input               reset
);
  assign rsp_valid = cmd_valid;
  assign cmd_ready = rsp_ready;
  assign rsp_payload_ready = 1'b1;

  localparam [8:0] RED_POLY = 9'h11B;

  function [7:0] gf_mul8;
    input [7:0] a;
    input [7:0] b;
    reg [15:0] prod;
    integer i;
    begin
      prod = 16'h0;
      for (i = 0; i < 8; i = i + 1) begin
        if (b[i])
          prod = prod ^ ( {8'h00, a} << i );
      end
      for (i = 15; i >= 8; i = i - 1) begin
        if (prod[i]) begin
          prod = prod ^ ( {7'h00, RED_POLY} << (i - 8) );
        end
      end
      gf_mul8 = prod[7:0];
    end
  endfunction

  wire [7:0] a0 = cmd_payload_inputs_0[7:0];
  wire [7:0] b0 = cmd_payload_inputs_1[7:0];
  wire [7:0] prod0 = gf_mul8(a0, b0);

  wire [7:0] a1 = cmd_payload_inputs_0[15:8];
  wire [7:0] a2 = cmd_payload_inputs_0[23:16];
  wire [7:0] a3 = cmd_payload_inputs_0[31:24];
  wire [7:0] b1 = cmd_payload_inputs_1[15:8];
  wire [7:0] b2 = cmd_payload_inputs_1[23:16];
  wire [7:0] b3 = cmd_payload_inputs_1[31:24];

  wire [7:0] prod1 = gf_mul8(a1, b1);
  wire [7:0] prod2 = gf_mul8(a2, b2);
  wire [7:0] prod3 = gf_mul8(a3, b3);

  wire [31:0] vec_out = {prod3, prod2, prod1, prod0};

  assign rsp_payload_outputs_0 = cmd_payload_function_id[0] ? vec_out : {24'h0, prod0};

endmodule
