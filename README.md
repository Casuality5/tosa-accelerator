# DMA CONTROLLER (DESIGN AND VERIFICATION STAGE)  (ver 0.1)

## OVERVIEW

Contains 6 State FSM

1. IDLE      - Wait Till BUS_WRITE_EN is Asserted       
2. FETCH     - Fetch Vector and Patch from BUS and write to SRAM
3. DISPATCH  - Gives Signals to Data Dispatcher to Forward Data to Other Blocks in Pipeline
4. WAIT      - Wait till the Score is Ready 
5. SEND      - Send Score to the BUS
6. DONE      - Send Interrupt Signal to VEGA

## ASSUMPTION

1. BUS_WRITE_EN must remain HIGH during transfer
2. 256- byte fixed burst
3. SCORE_DONE is ASYNC but stable

## Limitation
1. NO Synchronizer for SCORE_DONE
===========================================================================================
