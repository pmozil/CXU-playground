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
  input      [2047:0] state_read,
  output     [2047:0] state_write,
  output              state_write_en,
  input               clk,
  input               reset
);
  assign rsp_valid = 1;
  assign cmd_ready = 1;

  wire signed [7:0] a0 = cmd_payload_inputs_0[7:0];
  wire signed [7:0] a1 = cmd_payload_inputs_0[15:8];
  wire signed [7:0] a2 = cmd_payload_inputs_0[23:16];
  wire signed [7:0] a3 = cmd_payload_inputs_0[31:24];

  wire signed [7:0] b0 = cmd_payload_inputs_1[7:0];
  wire signed [7:0] b1 = cmd_payload_inputs_1[15:8];
  wire signed [7:0] b2 = cmd_payload_inputs_1[23:16];
  wire signed [7:0] b3 = cmd_payload_inputs_1[31:24];

  wire signed [15:0] prod0 = a0 * b0;
  wire signed [15:0] prod1 = a1 * b1;
  wire signed [15:0] prod2 = a2 * b2;
  wire signed [15:0] prod3 = a3 * b3;

  wire signed [31:0] dot_product = prod0 + prod1 + prod2 + prod3;

  assign rsp_payload_outputs_0 = cmd_payload_function_id[0] ? dot_product : 32'b0;
endmodule

