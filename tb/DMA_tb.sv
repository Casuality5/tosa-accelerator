module DMA_tb;

    // Clock & Reset
    logic CLK;
    logic RST;

    // Inputs
    logic [7:0] BUS_INCOMING_VECTOR;
    logic [7:0] BUS_INCOMING_PATCH;
    logic BUS_WRITE_EN;
    logic SCORE_DONE;
    logic [7:0] SCORE_IN;

    // Outputs
    logic SRAM_WRITE_EN;
    logic [7:0] SRAM_WRITE_ADDRESS;
    logic [15:0] SRAM_WRITE_DATA;
    logic DISPATCH_EN;
    logic [7:0] SCORE_OUT;
    logic INTERRUPT;
    logic [2:0] STATE_OUT;

    // DUT
    DMA dut(
        .CLK(CLK),
        .RST(RST),
        .BUS_INCOMING_VECTOR(BUS_INCOMING_VECTOR),
        .BUS_INCOMING_PATCH(BUS_INCOMING_PATCH),
        .BUS_WRITE_EN(BUS_WRITE_EN),
        .SCORE_DONE(SCORE_DONE),
        .SCORE_IN(SCORE_IN),
        .SRAM_WRITE_EN(SRAM_WRITE_EN),
        .SRAM_WRITE_ADDRESS(SRAM_WRITE_ADDRESS),
        .SRAM_WRITE_DATA(SRAM_WRITE_DATA),
        .DISPATCH_EN(DISPATCH_EN),
        .SCORE_OUT(SCORE_OUT),
        .INTERRUPT(INTERRUPT),
        .STATE_OUT(STATE_OUT)
    );

    // ✅ Proper clock
    always #5 CLK = ~CLK;

    // ✅ Task for clean stimulus
    task send_data(input [7:0] vec, input [7:0] patch);
        @(posedge CLK);
        #1;
        BUS_INCOMING_VECTOR = vec;
        BUS_INCOMING_PATCH  = patch;
    endtask

    initial begin
        // Init everything
        CLK = 0;
        RST = 1;

        BUS_WRITE_EN = 0;
        BUS_INCOMING_VECTOR = 0;
        BUS_INCOMING_PATCH  = 0;
        SCORE_DONE = 0;
        SCORE_IN = 0;
        
     
        // Reset
        #20;
        RST = 0;
        
        @(posedge CLK);
        BUS_WRITE_EN = 1;
        // Send data
        for (int i = 1; i < 256; i++) begin
            send_data(i[7:0], i[7:0]);
        end
        
        // Stop write
        @(posedge CLK);
        BUS_WRITE_EN = 0;

        // Wait
        #3000;
        #17;
        SCORE_DONE = 1;
        SCORE_IN = 8'haf;
        
        @(posedge CLK);
        SCORE_DONE = 0;
        INTERRUPT = 1;

        $finish;
    end

endmodule