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


  wire [31:0] mul    = $signed(cmd_payload_inputs_0) * $signed(cmd_payload_inputs_1);

  wire [31:0] mulsh  = $signed(mul) >>> 10;

  assign rsp_payload_outputs_0 = mulsh;
endmodule
