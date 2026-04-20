; SAP-1 Demo Program: JUMP + ROTATE
; ===================================
; Loads two values, jumps to a rotate
; routine, performs ROL/ROR on both
; registers, then stores A+B and A-B.
;
; Expected results:
;   A = 0x2C (44), B = 0x07 (7)
;   M[0xC] = 0x33 (51) = A+B
;   M[0xD] = 0x25 (37) = A-B

ORG 0
LDA  1110       ; A <- M[0xE] = 0x2C (44)
LDB  1111       ; B <- M[0xF] = 0x07 (7)
JUMP 0011       ; jump to rotate routine at 0x3

ORG 3
ROL_A           ; A: 0x2C (00101100) -> 0x58 (01011000)
ROL_B           ; B: 0x07 (00000111) -> 0x0E (00001110)
ROR_A           ; A: 0x58 (01011000) -> 0x2C (00101100)  back to original
ROR_B           ; B: 0x0E (00001110) -> 0x07 (00000111)  back to original
STA  1100       ; M[0xC] <- A+B = 44+7 = 51 (0x33)
STS  1101       ; M[0xD] <- A-B = 44-7 = 37 (0x25)
HLT             ; halt

ORG 14
DATA 00101100   ; 0x2C = 44  (operand for LDA)
DATA 00000111   ; 0x07 = 7   (operand for LDB)
