module DMA(
    input   logic CLK,
    input   logic RST,
    input   logic [7:0] BUS_INCOMING_VECTOR,  // BUS DATA IN
    input   logic [7:0] BUS_INCOMING_PATCH,
    input   logic BUS_WRITE_EN,               // SIGNAL FROM VEGA ASKING TO STORE OR IGNORE THE DATA
    input   logic SCORE_DONE,
    input   logic [7:0] SCORE_IN,
    output  logic SRAM_WRITE_EN,
    output  logic [7:0] SRAM_WRITE_ADDRESS,
    output  logic [15:0] SRAM_WRITE_DATA,
    output  logic DISPATCH_EN,
    output  logic [7:0] SCORE_OUT,
    output  logic INTERRUPT,
    output  logic [2:0] STATE_OUT               // FOR DEBUGGING
);

logic [7:0] VECTOR_OUT;  // SIGNALS FOR
logic [7:0] PATCH_OUT;    // SKID REGISTER



always_ff @(posedge CLK or posedge RST) begin : SKID_REGISTER

    if (RST) begin
        {VECTOR_OUT, PATCH_OUT} <= 0;
    end
    else begin
        {VECTOR_OUT, PATCH_OUT} <= {BUS_INCOMING_VECTOR, BUS_INCOMING_PATCH};
    end
end


typedef enum logic [2:0] { 
    IDLE,
    FETCH,
    DISPATCH,
    WAIT,
    SEND,
    DONE
 } STATES ;
STATES CURRENT_STATE, NEXT_STATE;

assign STATE_OUT = CURRENT_STATE;

always_ff @( posedge CLK or posedge RST ) begin : STATE_TRANSITIONING

    if(RST) CURRENT_STATE   <= IDLE;

    else    CURRENT_STATE   <= NEXT_STATE;    
end



logic [7:0] BYTE_COUNT;
always_ff @(posedge CLK or posedge RST) begin : BYTE_COUNTER

    if(RST) BYTE_COUNT <= 0;

    else if(CURRENT_STATE == FETCH && BUS_WRITE_EN) begin
    BYTE_COUNT <= BYTE_COUNT + 1;
    //SRAM_WRITE_EN <= 1;
    end
    
    else if(CURRENT_STATE == IDLE) SRAM_WRITE_EN <= 0;
    
    else if(CURRENT_STATE == FETCH && BUS_WRITE_EN == 0) begin
        if (SRAM_WRITE_EN == 1) BYTE_COUNT <= BYTE_COUNT + 1;
    //SRAM_WRITE_EN <= 0;
        else BYTE_COUNT <= 0;
    end
        
    else if (CURRENT_STATE == DISPATCH) BYTE_COUNT <= 0;
end


always_comb begin : STATE_DETERMINATION
    SRAM_WRITE_EN      = 0;
    SRAM_WRITE_ADDRESS = 0;
    SRAM_WRITE_DATA    = 0;
    DISPATCH_EN        = 0;
    SCORE_OUT          = 0;
    INTERRUPT          = 0;

    case (CURRENT_STATE)

        IDLE    :   begin
                    if (BUS_WRITE_EN)
                    NEXT_STATE = FETCH;
                    
                    else begin
                    NEXT_STATE = IDLE;
                    SRAM_WRITE_EN = 0;
                    end
                    end

        FETCH   :   begin
        
                    if (!BUS_WRITE_EN && BYTE_COUNT != 8'hff) begin
                    NEXT_STATE = IDLE;
                    SRAM_WRITE_EN = 1;
                    SRAM_WRITE_ADDRESS = BYTE_COUNT;
                    SRAM_WRITE_DATA = {VECTOR_OUT, PATCH_OUT};
                    end
                    else begin
                    SRAM_WRITE_EN = 1;
                    SRAM_WRITE_DATA = {VECTOR_OUT, PATCH_OUT};
                    SRAM_WRITE_ADDRESS = BYTE_COUNT;
                    if (BYTE_COUNT == 8'hff && SRAM_WRITE_EN == 1)
                    NEXT_STATE = DISPATCH;
                    else
                    NEXT_STATE = FETCH;
                    end
                    end

        DISPATCH:   begin
                    SRAM_WRITE_EN = 0;
                    SRAM_WRITE_DATA = 0;
                    DISPATCH_EN = 1;
                    NEXT_STATE = WAIT;
                    end

        
        WAIT    :   begin 
                    if (SCORE_DONE)
                    NEXT_STATE = SEND;
                    else
                    NEXT_STATE = WAIT;
                    end


        SEND    :   begin
                    SCORE_OUT = SCORE_IN;
                    NEXT_STATE = DONE;
                    end


        DONE    :   begin
                    INTERRUPT = 1;
                    NEXT_STATE = IDLE;
                    end
        default:    NEXT_STATE = IDLE;
    endcase
end
endmodule