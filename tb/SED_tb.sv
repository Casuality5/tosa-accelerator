module SED_tb;

    logic signed [15:0] TASK_EMBEDDED_VECTOR [0:15];
    logic signed [15:0] VISUAL_EMBEDDED_VECTOR [0:15];
    logic signed [35:0] DOT_OUT;

    SED dut (
        .TASK_EMBEDDED_VECTOR(TASK_EMBEDDED_VECTOR),
        .VISUAL_EMBEDDED_VECTOR(VISUAL_EMBEDDED_VECTOR),
        .DOT_OUT(DOT_OUT)
    );

    initial begin
        integer i;
        for (i = 0; i < 16; i = i + 1) begin
            TASK_EMBEDDED_VECTOR[i] = 0;
            VISUAL_EMBEDDED_VECTOR[i] = 0;
        end

        // Simple test
        TASK_EMBEDDED_VECTOR[0] = 1;
        TASK_EMBEDDED_VECTOR[1] = 2;
        TASK_EMBEDDED_VECTOR[2] = 3;
        TASK_EMBEDDED_VECTOR[3] = 4;
        TASK_EMBEDDED_VECTOR[4] = 2;
        TASK_EMBEDDED_VECTOR[5] = -1;



        VISUAL_EMBEDDED_VECTOR[0] = 1;
        VISUAL_EMBEDDED_VECTOR[1] = 2;
        VISUAL_EMBEDDED_VECTOR[2] = 3;
        VISUAL_EMBEDDED_VECTOR[3] = 4;
        VISUAL_EMBEDDED_VECTOR[4] = 1;
        VISUAL_EMBEDDED_VECTOR[5] = 4;
        
        #10;
        $display("DOT = %0d", DOT_OUT); 

        $finish;
    end

endmodule