module ARRAY(
    input logic CLK,
    input logic RST,
    input logic EN,
    input logic CLR,
    input logic [7:0] V_IN[0:15],
    input logic [7:0] P_IN[0:15],
    output logic [31:0] GAP_OUT [0:15]
);
logic [7:0] V_WIRE [0:15][0:16];
logic [7:0] P_WIRE [0:16][0:15];
logic [31:0] ACC_WIRE[0:15][0:15];
genvar i,j;
generate
    for (i = 0; i < 16; i++) begin : ROW
        for (j = 0; j < 16; j++) begin : COL
            PE pe_inst(
                .CLK(CLK),
                .RST(RST),
                .EN(EN),
                .CLR(CLR),
                .V_ELEMENT_IN(j == 0 ? V_IN[i] : V_WIRE[i][j]),
                .P_ELEMENT_IN(i == 0 ? P_IN[j]  : P_WIRE[i][j]),
                .V_ELEMENT_OUT(V_WIRE[i][j+1]),
                .P_ELEMENT_OUT(P_WIRE[i+1][j]),
                .CLIPPED_ACCUMULATE(ACC_WIRE[i][j])
            );
        end
    end

        assign GAP_OUT[i] = (
            ACC_WIRE[i][0]  + ACC_WIRE[i][1]  + ACC_WIRE[i][2]  +
            ACC_WIRE[i][3]  + ACC_WIRE[i][4]  + ACC_WIRE[i][5]  +
            ACC_WIRE[i][6]  + ACC_WIRE[i][7]  + ACC_WIRE[i][8]  +
            ACC_WIRE[i][9]  + ACC_WIRE[i][10] + ACC_WIRE[i][11] +
            ACC_WIRE[i][12] + ACC_WIRE[i][13] + ACC_WIRE[i][14] +
            ACC_WIRE[i][15]
        ) >> 4;

endgenerate
endmodule

module PE(
    input   logic                   CLK,
    input   logic                   RST,
    input   logic                   EN,
    input   logic                   CLR,
    input   logic           [7:0]   V_ELEMENT_IN,
    input   logic           [7:0]   P_ELEMENT_IN,
    output  logic           [7:0]   V_ELEMENT_OUT,
    output  logic           [7:0]   P_ELEMENT_OUT,
    output  logic signed    [31:0]  CLIPPED_ACCUMULATE
);
logic            [7:0] P_REG, V_REG;
logic signed    [31:0]  ACCUMULATE;

always_ff @(posedge CLK or posedge RST) begin : PE_CELL
    if(RST) begin
        P_REG           <= 0;
        V_REG           <= 0;
        ACCUMULATE      <= 0;
    end
    else begin
        if (CLR) ACCUMULATE <= 0;
        else if (EN) ACCUMULATE <= ACCUMULATE + $signed({1'b0, V_REG}) * $signed({1'b0, P_REG});

        if (EN) begin
            V_REG <= V_ELEMENT_IN;
            P_REG <= P_ELEMENT_IN;
        end
    end
end

assign V_ELEMENT_OUT = V_REG;
assign P_ELEMENT_OUT = P_REG;
assign CLIPPED_ACCUMULATE = (ACCUMULATE[31] ? 32'sd0 : ACCUMULATE) // ReLU


endmodule