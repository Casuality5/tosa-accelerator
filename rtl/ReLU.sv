module ReLU(
    input  logic signed [31:0] DATA_IN,
    output logic signed [31:0] DATA_OUT
);

assign DATA_OUT = (DATA_IN[31] ? 32'sd0 : DATA_IN);
endmodule