module Cxu1 (
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
  assign rsp_valid = cmd_valid;
  assign cmd_ready = rsp_ready;


  wire [31:0] mul    = $signed(cmd_payload_inputs_0) * $signed(cmd_payload_inputs_1);

  assign rsp_payload_outputs_0 = mul;
endmodule
