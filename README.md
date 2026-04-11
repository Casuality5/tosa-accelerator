# 1. DMA CONTROLLER (DESIGN AND VERIFICATION STAGE)  (ver 0.1)

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
# 2. SED (DESIGN AND VERIFICATION STAGE)  (ver 0.1)

## OVERVIEW

This module implements a 16-element vector dot product engine
(signed fixed-point) using parallel multipliers and an adder tree.

## ASSUMPTION

1. Input vectors are of fixed length = 16
2. Each element is 16-bit signed (two’s complement)
3. Both input vectors are available simultaneously (no streaming)
4. Inputs remain stable during computation (combinational design)
5. No overflow beyond allocated bit-width (36-bit output assumed sufficient)
6. Multiplication and addition are ideal (no hardware delay modeled)
7. No invalid/X/Z values present in simulation inputs

## LIMITATION

1. Fully combinational → long critical path (not timing friendly)
2. No pipelining → not suitable for high-frequency hardware yet
3. Fixed vector size (16) → not scalable without redesign
4. Single dot product at a time → no parallel multi-object support
5. No overflow handling or saturation logic
6. No clock/reset usage → not integrated into synchronous systems
7. Resource heavy → 16 multipliers used simultaneously
8. No normalization (not cosine similarity, only raw dot product)
===========================================================================================
# 3. ReLU (DESIGN AND VERIFICATION STAGE) (ver 0.1)

## OVERVIEW

This module is pure combinational that receives a signed 32 bit value from PE accumulator and clips anyu negative value to zero.

## ASSUMPTION

1. Input is a signed 32-bit value representing a fully accumulated PE result — ReLU is not applied mid-accumulation
2. Zero is treated as non-negative — input of 0 produces output of 0 (pass through)
3. ReLU is instantiated once per PE — PE Array contains 256 ReLU instances, one per accumulator output

## LIMITATION

1. No support for Leaky ReLU or parametric variants — threshold is hardcoded to zero
2. No valid/ready handshaking — downstream GAP module must know when to sample output
3. Fixed 32-bit width — if PE accumulator width changes, ReLU width must be manually updated. Parameterization is a planned future improvement
4. No saturation logic — if upstream PE accumulator overflows before reaching ReLU, result will be incorrect. Overflow prevention is PE Array's responsibility
===========================================================================================
