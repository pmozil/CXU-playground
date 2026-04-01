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
  // Tie off readiness and state since we're entirely combinatorial & stateless
  assign cmd_ready = 1'b1;
  assign rsp_valid = 1'b1;
  assign rsp_payload_ready = 1'b1;
  assign state_write_en = 1'b0;
  assign state_write = 2048'b0;

  wire [31:0] rs1 = cmd_payload_inputs_0;
  wire [31:0] rs2 = cmd_payload_inputs_1;

  // ------------------------------------------------------------------------
  // FN 0: cxu_bitrev - Reverses 32 bits
  // ------------------------------------------------------------------------
  wire [31:0] bitrev;
  genvar i;
  generate
    for (i = 0; i < 32; i = i + 1) begin : gen_bitrev
      assign bitrev[i] = rs1[31 - i];
    end
  endgenerate

  // ------------------------------------------------------------------------
  // FN 2: cxu_mask - Returns (1 << n) - 1
  // ------------------------------------------------------------------------
  wire [31:0] mask = (32'h1 << rs1[4:0]) - 32'h1;

  // ------------------------------------------------------------------------
  // FN 3: cxu_huft_idx - Returns rs1 & ((1 << rs2) - 1)
  // ------------------------------------------------------------------------
  wire [31:0] huft_idx = rs1 & ((32'h1 << rs2[4:0]) - 32'h1);

  // ------------------------------------------------------------------------
  // FN 4: cxu_copy_addr - Fused back-reference address calculation
  // rs1[31:16] = w, rs1[15:0] = dist_base
  // rs2 = extra_val
  // ------------------------------------------------------------------------
  wire [15:0] w         = rs1[31:16];
  wire [15:0] dist_base = rs1[15:0];
  wire [15:0] extra_val = rs2[15:0];
  wire [31:0] copy_addr = {16'h0, (w - dist_base - extra_val) & 15'h7FFF};

  // ------------------------------------------------------------------------
  // Output Mux
  // ------------------------------------------------------------------------
  reg [31:0] result;
  always @(*) begin
    case (cmd_payload_function_id)
      3'd0: result = bitrev;
      3'd2: result = mask;
      3'd3: result = huft_idx;
      3'd4: result = copy_addr;
      default: result = 32'h0;
    endcase
  end

  assign rsp_payload_outputs_0 = result;

endmodule
