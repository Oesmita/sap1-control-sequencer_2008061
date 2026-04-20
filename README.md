# SAP-1 Architecture with Control Sequencer

> **Course:** ETE 404 — VLSI Technology Sessional  
> **Institution:** Chittagong University of Engineering and Technology (CUET)  
> **Department:** Electronics and Telecommunication Engineering  
> **Student:** Oesmita Chakma Moon | ID: 2008061  
> **Supervisor:** Arif Istiaque, Lecturer, Dept. of ETE, CUET

---

## Overview

A complete, enhanced **SAP-1 (Simple-As-Possible) microprocessor** implemented in **Logisim Evolution**, featuring:

- Hardwired Control Sequencer (no microprogramming)
- ROM-to-RAM Auto-Bootloader (2-phase handshake)
- Python Assembler (`sap1_asm.py`)
- 9-instruction ISA with arithmetic, rotate, jump, and halt operations
- Dual operating modes: **Automatic** and **Manual/Loader**

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Key Features](#key-features)
- [Instruction Set Architecture](#instruction-set-architecture)
- [Module Breakdown](#module-breakdown)
- [Fetch–Decode–Execute Cycle](#fetchdecodeexecute-cycle)
- [Bootloader Operation](#bootloader-operation)
- [Python Assembler](#python-assembler)
- [Running a Program](#running-a-program)
- [Project Structure](#project-structure)
- [Demo](#demo)

---

## Architecture Overview

The processor uses a **single 8-bit data bus** with a **4-bit address space** (16 memory locations). Tri-state logic guarantees that only one module drives the bus at any time.

```
 ┌──────────────────────────────────────────────┐
 │              8-bit Data Bus                  │
 └──┬──────┬──────┬──────┬──────┬──────┬───────┘
    │      │      │      │      │      │
   PC    SRAM   Reg A  Reg B   ALU   Rotater
    │      │      │      │      │      │
    └──────┴──────┴──────┴──────┴──────┘
                    ▲
             Control Sequencer
           (6-phase Ring Counter)
```

**Bus Drivers:** `pc_out`, `sram_rd`, `a_out`, `b_out`, `alu_out`, `rotater_out`, `address_out_en`  
**Bus Receivers:** `mar_in_en`, `a_in`, `b_in`, `sram_wr`, `ins_reg_in_en`, `pc_load`

---

## Key Features

| Feature | Description |
|---|---|
| **Architecture** | Enhanced SAP-1, single-bus, 8-bit datapath |
| **Address Space** | 4-bit → 16 memory locations |
| **Control** | Hardwired (no microprogramming) |
| **Timing** | 6-phase ring counter (T1–T6) |
| **Registers** | Dual 8-bit GP registers (A & B) |
| **Memory** | 16×8 SRAM + ROM bootloader |
| **ALU** | Ripple-carry adder + bidirectional shifter |
| **Modes** | Automatic & Manual/Loader |
| **Assembler** | Python-based, outputs Logisim ROM image |

---

## Instruction Set Architecture

Instructions are 8-bit: upper nibble = **opcode**, lower nibble = **operand/address**.

| Mnemonic | Opcode (bin) | Hex | Operand | Description |
|---|---|---|---|---|
| `LDA addr` | `0001` | `1` | yes | Load memory → Register A |
| `LDB addr` | `0010` | `2` | yes | Load memory → Register B |
| `STA addr` | `0011` | `3` | yes | Store (A + B) → memory |
| `STS addr` | `0100` | `4` | yes | Store (A − B) → memory |
| `ROR_A` | `0110` | `6` | no | Rotate A right by 1 bit |
| `ROR_B` | `0111` | `7` | no | Rotate B right by 1 bit |
| `ROL_A` | `1000` | `8` | no | Rotate A left by 1 bit |
| `ROL_B` | `1001` | `9` | no | Rotate B left by 1 bit |
| `JUMP addr` | `1010` | `A` | yes | Unconditional jump |
| `HLT` | `1011` | `B` | no | Halt processor |

> **Note:** `STA` and `STS` implement *arithmetic-on-store* semantics — they compute A+B or A−B and write the result directly to memory, enabling in-place results without an explicit ADD/SUB opcode.

---

## Module Breakdown

### Registers A & B
- Two 8-bit flip-flop-based registers
- Independent enable lines (`a_in`, `b_in`, `a_out`, `b_out`)
- Internal direct connection to ALU (no bus overhead)

### Program Counter (PC)
- 4-bit register; supports sequential increment and direct load (JUMP)
- `T1`: outputs current address → MAR
- `T2`: increments (`pc_en = 1`)
- `JUMP`: loads `IR[3:0]` directly (`pc_load = 1`)

### Memory System (MAR + SRAM)
- 4-bit MAR captures target address
- 16×8 SRAM with `sram_rd` / `sram_wr` control
- `T1`: MAR ← PC (instruction fetch)
- `T4`: MAR ← IR[3:0] (operand addressing)

### Instruction Register & Opcode Decoder
- IR splits instruction into: `IR[7:4]` = opcode, `IR[3:0]` = operand
- 4-to-16 one-hot decoder drives the control sequencer
- `T2`: IR ← M[MAR]

### ALU
- 8-bit ripple-carry adder (A + B or A − B)
- Bidirectional barrel shifter controlled by `shift_out` + `right_or_left`
- Inputs wired directly from register internals

### Timing Control Generator
- 6-phase ring counter (T1 → T6, then wraps)
- Each state activates specific micro-operation signals
- `HLT` disables the counter permanently

### Bootloader (ROM → RAM)
- 2-phase FSM:  
  - **Phase 1:** Drive address onto bus, latch into MAR  
  - **Phase 2:** Drive ROM data onto bus, write to SRAM, increment counter
- Transfers all 16 bytes (0x0–0xF) in 32 clock pulses
- All CU outputs are ANDed with `cs_en`, guaranteeing no bus contention

---

## Fetch–Decode–Execute Cycle

```
T1: pc_out, mar_in_en        → MAR ← PC
T2: sram_rd, ins_reg_in_en   → IR  ← M[MAR]
    pc_en                    → PC  ← PC + 1
T3: ins_reg_out_en, mar_in_en→ MAR ← IR[3:0]  (all instructions)
T4: <instruction-specific>   (see table below)
```

| Instruction | T4 Operation |
|---|---|
| `LDA` | `sram_rd, a_in` → A ← M[MAR] |
| `LDB` | `sram_rd, b_in` → B ← M[MAR] |
| `STA` | `alu_out, sram_wr` → M[MAR] ← A+B |
| `STS` | `alu_out(sub), sram_wr` → M[MAR] ← A−B |
| `ROL_A` | `ro_out_en, rotater_out, right_or_left` → A rotated left |
| `ROR_A` | `ro_out_en, rotater_out` → A rotated right |
| `ROL_B` | `ro_out_en, rotater_out, right_or_left, rotate_reg_en` → B rotated left |
| `ROR_B` | `ro_out_en, rotater_out, rotate_reg_en` → B rotated right |
| `JUMP` | `address_out_en, pc_load` → PC ← IR[3:0] |
| `HLT` | `hlt_set = 1` → ring counter disabled |

---

## Bootloader Operation

```
debug = 1  →  Bootloader active, CU masked (cs_en = 0)
              Phase 1: address bus → MAR
              Phase 2: ROM data → SRAM, CTR++
              (repeat for all 16 addresses)

debug = 0  →  Bootloader tri-states off
cs_en = 1  →  CU enabled, pc_reset to 0000, run!
```

---

## Python Assembler

Located at [`assembler/sap1_asm.py`](assembler/sap1_asm.py).

### Syntax

```asm
; Comments with ; or #
ORG 0          ; set program counter origin (0–15)
LDA 1110       ; operands: binary, decimal, or hex (e.g. 0xE or E)
LDB 1111
JUMP 0011
ORG 3
ROL_A
ROR_B
STA 1100
HLT
ORG 14
DATA 00101100  ; raw 8-bit data byte
DATA 00000111
```

### Usage

```bash
python assembler/sap1_asm.py program.asm
```

**Output:** 16 hex bytes (one per address 0x0–0xF) for direct paste into Logisim ROM editor.

**Encoding:** `byte = (opcode << 4) | operand`

### Example Output

```
Input:  LDA 0xE → opcode=0001, operand=1110 → 0x1E
Output: 1E 2F A3 80 90 60 70 3C 4D B0 00 00 00 00 2C 07
```

---

## Running a Program

### Step-by-Step

1. **Write assembly** → assemble with `sap1_asm.py` → copy hex output
2. **Open Logisim** → right-click ROM → *Edit Contents* → paste hex bytes
3. **Load to RAM:**
   - Set `debug = HIGH`
   - Toggle clock until all 16 bytes are transferred (32 clock pulses)
   - Set `debug = LOW`
4. **Execute:**
   - Pulse `pc_reset` → PC = 0000
   - Set `cs_en = HIGH`
   - Apply clock pulses → CPU runs automatically until `HLT`

### Demo Program (JUMP + ROTATE)

```asm
ORG 0
LDA 1110       ; A ← 0x2C (44)
LDB 1111       ; B ← 0x07 (7)
JUMP 0011      ; jump to rotate routine

ORG 3
ROL_A          ; A: 0x2C → 0x58
ROL_B          ; B: 0x07 → 0x0E
ROR_A          ; A: 0x58 → 0x2C
ROR_B          ; B: 0x0E → 0x07
STA 1100       ; M[0xC] ← A+B = 44+7 = 51 (0x33)
STS 1101       ; M[0xD] ← A-B = 44-7 = 37 (0x25)
HLT

ORG 14
DATA 00101100  ; 0x2C = 44
DATA 00000111  ; 0x07 = 7
```

**Expected final state:**

| Signal | Value |
|---|---|
| Register A | `0x2C` (44) |
| Register B | `0x07` (7) |
| M[0xC] | `0x33` (51) = A+B |
| M[0xD] | `0x25` (37) = A−B |
| PC | halted |

---

## Project Structure

```
sap1-control-sequencer_2008061/
│
├── README.md
├── LICENSE
│
├── assembler/
│   ├── sap1_asm.py          # Python assembler
│   └── examples/
│       ├── jump_rotate.asm  # Demo program
│       └── jump_rotate.hex  # Assembled output
│
├── logisim/
│   └── sap1_2008061.circ    # Main Logisim Evolution circuit file
│
├── docs/
│   ├── project_report.pdf   # Full project report (PDF)
│   └── architecture.md      # Extended architecture notes
│
└── assets/
    └── (screenshots from the report)
```

---

## Demo

- 📺 **YouTube Demo:** [Watch here](https://youtu.be/<your-video-id>)
- 🔗 **GitHub:** [sap1-control-sequencer_2008061](https://github.com/Oesmita/sap1-control-sequencer_2008061)

---

## References

- Malvino, A. P. *Digital Computer Electronics*. McGraw-Hill.
- Logisim-Evolution: [github.com/logisim-evolution/logisim-evolution](https://github.com/logisim-evolution/logisim-evolution)

---

*Submitted as part of ETE 404 — VLSI Technology Sessional, CUET.*
