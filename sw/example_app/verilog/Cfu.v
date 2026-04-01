// Copyright 2021 The CFU-Playground Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.



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
  // Trivial handshaking for a combinational CFU
  assign rsp_valid = cmd_valid;
  assign cmd_ready = rsp_ready;
  // assign rsp_valid = 1;
  // assign cmd_ready = 1;


  wire [31:0] mul    = $signed(cmd_payload_inputs_0) * $signed(cmd_payload_inputs_1);

  wire [31:0] mulsh  = $signed(mul) >>> 10;

  assign rsp_payload_outputs_0 = cmd_payload_function_id[0] ? mul : mulsh;


endmodule
