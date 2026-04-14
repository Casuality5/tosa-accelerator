module SED( 
    input logic signed  [15:0] TASK_EMBEDDED_VECTOR [0:15],
    input logic signed [15:0] VISUAL_EMBEDDED_VECTOR [0:15],
    output logic signed [35:0] DOT_OUT
);

logic signed [31:0] P [0:15];
logic signed [35:0] S [0:15];
genvar i,j;

// ADDER TREE
generate
    for (i = 0; i < 16 ;i++) begin
        assign P[i] = TASK_EMBEDDED_VECTOR[i]*VISUAL_EMBEDDED_VECTOR[i]; // PARALLEL DOT
    end
    for (j = 0; j < 8; j ++) begin
        assign S[j]    = P[2*j] + P[2*j + 1]; // LVL 1
    end
    for (j = 0; j < 4; j ++ ) begin
        assign S[j+8] = S[2*j] + S[2*j + 1];  // LVL 2
    end
endgenerate

assign S[12] = S[8] + S[9];     // LVL 3
assign S[13] = S[10]+ S[11];    // LVL 3
assign DOT_OUT = S[12] + S[13]; // LVL 4

endmodule