`timescale 1ns/1ps

module ARRAY_tb;

    logic        CLK, RST, EN, CLR;
    logic [7:0]  V_IN [0:15];
    logic [7:0]  P_IN [0:15];
    logic [31:0] GAP_OUT [0:15];

    // Reference matrices for skewing
    logic [7:0] V_data [0:15][0:15];
    logic [7:0] P_data [0:15][0:15];

    ARRAY dut(
        .CLK    (CLK),
        .RST    (RST),
        .EN     (EN),
        .CLR    (CLR),
        .V_IN   (V_IN),
        .P_IN   (P_IN),
        .GAP_OUT(GAP_OUT)
    );

    // Clock Generation
    always #5 CLK = ~CLK;

    initial begin
        // Initialize
        CLK = 0; RST = 1; EN = 0; CLR = 0;
        for (int i = 0; i < 16; i++) begin
            V_IN[i] = 0;
            P_IN[i] = 0;
            for (int j = 0; j < 16; j++) begin
                V_data[i][j] = 8'd2; // Value 'A'
                P_data[i][j] = 8'd2; // Value 'B'
            end
        end

        // Reset and Clear
        repeat(2) @(posedge CLK);
        RST = 0;
        CLR = 1;
        @(posedge CLK);
        CLR = 0;
        EN  = 1;

        for (int t = 0; t < 64; t++) begin
            for (int i = 0; i < 16; i++) begin
                if (t >= i && t < i + 16) 
                    V_IN[i] = V_data[i][t-i];
                else 
                    V_IN[i] = 0;

                if (t >= i && t < i + 16) 
                    P_IN[i] = P_data[t-i][i];
                else 
                    P_IN[i] = 0;
            end
            @(posedge CLK);
        end

        EN = 0;
        repeat(5) @(posedge CLK);
        $display("--- Starting Verification ---");
        for (int i = 0; i < 16; i++) begin
            if (GAP_OUT[i] == 32'd64)
                $display("[PASS] Row %0d: GAP_OUT = %0d", i, GAP_OUT[i]);
            else
                $display("[FAIL] Row %0d: GAP_OUT = %0d (Expected 64)", i, GAP_OUT[i]);
        end

        $finish;
    end

endmodule