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
  assign rsp_payload_ready = 1;

  wire do_increment =
        (cmd_payload_inputs_0 == 32'd10) &&
        (cmd_payload_inputs_1 == 32'd10);

  // Condition
  wire do_increment =
      (cmd_payload_inputs_0 == 32'd10) &&
      (cmd_payload_inputs_1 == 32'd10);

  // Byte-wise increment result
  wire [2047:0] incremented_state;

  genvar i;
  generate
    for (i = 0; i < 256; i = i + 1) begin : BYTE_INC
      assign incremented_state[i*8 +: 8] =
          state_read[i*8 +: 8] + 8'd1;
    end
  endgenerate
endmodule
