###### **Assembly language:**



ORG 0

LDA 1110         #; A = M\[1110]

LDB 1111         #; B = M\[1111]

STA 1100         #; M\[1100] = A + B

STS 1101         #; M\[1101] = A - B

HLT



ORG 14

DATA 00000101    #; M\[1110] = 5

DATA 00000011    #; M\[1111] = 3

ASM



**Hex Values:**



1E 2F 3C 4D B0 00 00 00 00 00 00 00 00 00 05 03









