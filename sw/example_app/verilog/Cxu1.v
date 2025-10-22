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
  input               clk,
  input               reset
);

  assign rsp_valid = cmd_valid;
  assign cmd_ready = rsp_ready;
  assign rsp_payload_ready = cmd_payload_ready;

  //  byte sum (unsigned)
  wire [31:0] cxu0;
  assign cxu0[31:0] =  cmd_payload_inputs_0[7:0]   + cmd_payload_inputs_1[7:0] +
                       cmd_payload_inputs_0[15:8]  + cmd_payload_inputs_1[15:8] +
                       cmd_payload_inputs_0[23:16] + cmd_payload_inputs_1[23:16] +
                       cmd_payload_inputs_0[31:24] + cmd_payload_inputs_1[31:24];

  // byte swap
  wire [31:0] cxu1;
  assign cxu1[31:24] =     cmd_payload_inputs_0[7:0];
  assign cxu1[23:16] =     cmd_payload_inputs_0[15:8];
  assign cxu1[15:8] =      cmd_payload_inputs_0[23:16];
  assign cxu1[7:0] =       cmd_payload_inputs_0[31:24];

  // bit reverse
  wire [31:0] cxu2;
  genvar n;
  generate
      for (n=0; n<32; n=n+1) begin
          assign cxu2[n] =     cmd_payload_inputs_0[31-n];
      end
  endgenerate

  // select output
  assign rsp_payload_outputs_0 = cmd_payload_function_id[1] ? cxu2 :
                                      ( cmd_payload_function_id[0] ? cxu1 : cxu0);

endmodule
