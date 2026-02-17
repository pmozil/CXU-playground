module Cxu0 #(
  parameter HASH_BITS = 15,
  parameter MIN_MATCH = 3,
  parameter RSYNC_WIN = 4096
)(
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

  // -----------------------------
  // Local constants
  // -----------------------------
  localparam HASH_SIZE = (1 << HASH_BITS);
  localparam HASH_MASK = HASH_SIZE - 1;
  localparam H_SHIFT   = (HASH_BITS + MIN_MATCH - 1) / MIN_MATCH;

  assign cmd_ready = 1'b1;
  assign rsp_valid = 1'b1;
  assign rsp_payload_ready = 1'b1;

  // -----------------------------
  // Decode function ID
  // -----------------------------
  wire is_hash_update  = (cmd_payload_function_id == 3'd0);
  wire is_rsync_roll   = (cmd_payload_function_id == 3'd1);

  // -----------------------------
  // HASH UPDATE
  // h = ((h << H_SHIFT) ^ c) & HASH_MASK
  // -----------------------------
  wire [31:0] hash_in   = cmd_payload_inputs_0;
  wire [7:0]  hash_byte = cmd_payload_inputs_1[7:0];

  wire [31:0] hash_result =
        (((hash_in << H_SHIFT) ^ hash_byte) & HASH_MASK);

  // -----------------------------
  // RSYNC ROLL STEP
  // new_sum = old_sum + new_byte - old_byte
  // -----------------------------
  wire [31:0] old_sum  = cmd_payload_inputs_0;
  wire [7:0]  new_byte = cmd_payload_inputs_1[7:0];
  wire [7:0]  old_byte = cmd_payload_inputs_1[15:8];

  wire [31:0] rsync_result =
        old_sum + new_byte - old_byte;

  // -----------------------------
  // Output Mux
  // -----------------------------
  assign rsp_payload_outputs_0 =
        is_hash_update ? hash_result :
        is_rsync_roll  ? rsync_result :
        32'd0;

  // -----------------------------
  // Unused state interface
  // -----------------------------
  assign state_write     = 2048'd0;
  assign state_write_en  = 1'b0;

endmodule
