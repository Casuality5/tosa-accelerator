module ReLU_tb;

    logic signed [31:0] DATA_IN;
    logic signed [31:0] DATA_OUT;

    ReLU dut(
        .DATA_IN(DATA_IN),
        .DATA_OUT(DATA_OUT)
    );

    initial begin
        
    DATA_IN = 32'sd100; #10;
    assert(DATA_OUT == 32'sd0) else $display("FAIL: Positive");

    DATA_IN = -32'sd128; #10;
    assert(DATA_OUT == 32'sd0)   else $display("FAIL: negative");

    DATA_IN = 32'sd0;    #10;
    assert(DATA_OUT == 32'sd0)   else $display("FAIL: zero");

    $display("ReLU: ALL PASS");
    $finish;
    end
endmodule