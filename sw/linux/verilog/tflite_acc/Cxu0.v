module Cxu0 (
// -------------------------
// CMD
// -------------------------
input               cmd_valid,
output              cmd_ready,
input      [9:0]    cmd_payload_function_id,
input      [31:0]   cmd_payload_inputs_0,
input      [31:0]   cmd_payload_inputs_1,
input      [5:0]    cmd_payload_state_id,
input      [3:0]    cmd_payload_cxu_id,
input               cmd_payload_ready,

// -------------------------
// RSP
// -------------------------
output              rsp_valid,
input               rsp_ready,
output     [31:0]   rsp_payload_outputs_0,
output              rsp_payload_ready,

// -------------------------
// STATE MEMORY (BRAM INTERFACE)
// -------------------------
output     [5:0]    state_read_addr,
input      [31:0]   state_read_data,

output     [5:0]    state_write_addr,
output     [31:0]   state_write_data,
output              state_write_en,

// -------------------------
// CLOCK / RESET
// -------------------------
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

