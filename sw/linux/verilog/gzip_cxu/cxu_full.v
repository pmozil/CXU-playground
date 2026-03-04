/* Cxu0.v — CXU extension for gzip/inflate bit-stream acceleration
 *
 * Function table (cmd_payload_function_id = funct3):
 *
 *  0  BITS_LOAD   — Append one byte into the bit-buffer.
 *                   rs1 = current packed state  {bk[7:0], bb[23:0]}
 *                   rs2 = next byte (low 8 bits)
 *                   returns new packed state    {bk[7:0], bb[23:0]}
 *
 *  1  BITS_PEEK   — Read n bits from the bit-buffer (no consume).
 *                   rs1 = packed state
 *                   rs2 = n  (0..16)
 *                   returns  bb & mask_bits[n]
 *
 *  2  BITS_DUMP   — Consume n bits from the bit-buffer.
 *                   rs1 = packed state
 *                   rs2 = n  (0..16)
 *                   returns new packed state
 *
 *  3  BITS_NEED   — Combined NEEDBITS helper: if bk >= n already, no-op;
 *                   otherwise caller must loop calling BITS_LOAD first.
 *                   rs1 = packed state
 *                   rs2 = n
 *                   returns 0 if bk >= n (ready), 1 if more bytes needed
 *
 *  4  HUFT_MASK   — Compute Huffman table index: rs1 & mask_bits[rs2]
 *                   rs1 = bit-buffer value (bb)
 *                   rs2 = number of bits (bl or bd)
 *                   returns masked index into huft table
 *
 *  5  SLIDE_WRAP  — Sliding-window index wrap: (rs1 + rs2) & 0x7FFF
 *                   rs1 = current window position w
 *                   rs2 = increment (0 for pure wrap, 1 for post-increment)
 *                   returns (rs1 + rs2) & (WSIZE-1)
 *
 *  6  PACK_STATE  — Pack bb and bk into one 32-bit word.
 *                   rs1 = bb  (bit buffer, low 24 bits used)
 *                   rs2 = bk  (bit count,  low  8 bits used)
 *                   returns  {bk[7:0], bb[23:0]}
 *
 *  7  UNPACK_STATE— Unpack field from packed state word.
 *                   rs1 = packed state
 *                   rs2 = 0 → return bb (sign-extended 24→32)
 *                         1 → return bk (zero-extended  8→32)
 *                   returns selected field
 *
 * Packed-state format (used by ops 0,1,2,3,6,7):
 *   bits [31:24] = bk  (number of valid bits in bb, 0..32)
 *   bits [23: 0] = bb  (bit buffer, low 24 bits; inflate never needs >24)
 *
 * Note: inflate's NEEDBITS loop only ever requests up to 16 bits at a time,
 * so 24 bits of bb storage is sufficient between LOAD calls.
 */

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

  // Always ready — combinational CXU, single-cycle latency
  assign rsp_valid          = 1'b1;
  assign cmd_ready          = 1'b1;
  assign state_write_en     = 1'b0;
  assign state_write        = 2048'b0;
  assign rsp_payload_ready  = 1'b1;

  // ── Unpack inputs ──────────────────────────────────────────────────────────
  wire [31:0] rs1 = cmd_payload_inputs_0;
  wire [31:0] rs2 = cmd_payload_inputs_1;
  wire [2:0]  fn  = cmd_payload_function_id;

  // Packed-state fields
  wire [7:0]  st_bk = rs1[31:24];          // bit count
  wire [23:0] st_bb = rs1[23:0];           // bit buffer

  // ── mask_bits[] ROM (0..16) ────────────────────────────────────────────────
  // mask_bits[n] = (1 << n) - 1
  function [15:0] mask_bits;
    input [4:0] n;
    mask_bits = (n == 0)  ? 16'h0000 :
                (n == 1)  ? 16'h0001 :
                (n == 2)  ? 16'h0003 :
                (n == 3)  ? 16'h0007 :
                (n == 4)  ? 16'h000f :
                (n == 5)  ? 16'h001f :
                (n == 6)  ? 16'h003f :
                (n == 7)  ? 16'h007f :
                (n == 8)  ? 16'h00ff :
                (n == 9)  ? 16'h01ff :
                (n == 10) ? 16'h03ff :
                (n == 11) ? 16'h07ff :
                (n == 12) ? 16'h0fff :
                (n == 13) ? 16'h1fff :
                (n == 14) ? 16'h3fff :
                (n == 15) ? 16'h7fff :
                            16'hffff ;   // n >= 16
  endfunction

  // ── Op 0: BITS_LOAD ────────────────────────────────────────────────────────
  // new_bb = st_bb | (byte << bk),  new_bk = bk + 8
  wire [31:0] load_bb_full = {8'b0, st_bb} | ({24'b0, rs2[7:0]} << st_bk);
  wire [7:0]  load_bk_new  = st_bk + 8;
  wire [31:0] load_result  = {load_bk_new, load_bb_full[23:0]};

  // ── Op 1: BITS_PEEK ────────────────────────────────────────────────────────
  wire [31:0] peek_result  = {16'b0, {16'b0, st_bb[15:0]} & {16'b0, mask_bits(rs2[4:0])}};

  // ── Op 2: BITS_DUMP ────────────────────────────────────────────────────────
  wire [23:0] dump_bb_new  = st_bb >> rs2[4:0];
  wire [7:0]  dump_bk_new  = st_bk - rs2[7:0];
  wire [31:0] dump_result  = {dump_bk_new, dump_bb_new};

  // ── Op 3: BITS_NEED ────────────────────────────────────────────────────────
  // returns 0 = ready, 1 = need more bytes
  wire [31:0] need_result  = (st_bk >= rs2[7:0]) ? 32'b0 : 32'b1;

  // ── Op 4: HUFT_MASK ────────────────────────────────────────────────────────
  // rs1 = bb, rs2 = bl/bd  →  bb & mask_bits[rs2]
  wire [31:0] huft_result  = {16'b0, rs1[15:0] & mask_bits(rs2[4:0])};

  // ── Op 5: SLIDE_WRAP ───────────────────────────────────────────────────────
  // (rs1 + rs2) & 0x7FFF  — keeps window pointer in [0, 32767]
  wire [31:0] slide_result = (rs1 + rs2) & 32'h00007FFF;

  // ── Op 6: PACK_STATE ───────────────────────────────────────────────────────
  wire [31:0] pack_result  = {rs2[7:0], rs1[23:0]};

  // ── Op 7: UNPACK_STATE ─────────────────────────────────────────────────────
  wire [31:0] unpack_result = rs2[0] ? {24'b0, rs1[31:24]}   // bk
                                     : {8'b0,  rs1[23:0]};   // bb

  // ── Output mux ────────────────────────────────────────────────────────────
  assign rsp_payload_outputs_0 =
      (fn == 3'h0) ? load_result   :
      (fn == 3'h1) ? peek_result   :
      (fn == 3'h2) ? dump_result   :
      (fn == 3'h3) ? need_result   :
      (fn == 3'h4) ? huft_result   :
      (fn == 3'h5) ? slide_result  :
      (fn == 3'h6) ? pack_result   :
                     unpack_result ;

endmodule
