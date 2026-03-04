module Cxu1 (
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
  output reg [2047:0] state_write,
  output reg          state_write_en,
  input               clk,
  input               reset
);

  assign cmd_ready = 1'b1;
  assign rsp_valid = cmd_valid;
  assign rsp_payload_ready = 1'b1;

  // ----------------------------------------------------
  // State handling
  // ----------------------------------------------------

  wire [5:0] word_index = cmd_payload_state_id;  // up to 64 entries
  wire [31:0] selected_word;

  // Extract selected 32-bit word
  assign selected_word = state_read[word_index * 32 +: 32];

  wire [31:0] updated_word = selected_word + 32'd10;

  integer i;

  always @(*) begin
    state_write     = state_read;
    state_write_en  = 1'b0;

    if (cmd_valid) begin
      state_write[word_index * 32 +: 32] = updated_word;
      state_write_en = 1'b1;
    end
  end

  // Return updated value as response
  assign rsp_payload_outputs_0 = updated_word;

endmodule
