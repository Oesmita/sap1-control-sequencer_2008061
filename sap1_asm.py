#!/usr/bin/env python3
"""
sap1_asm.py — SAP-1 Assembler
==============================
Converts SAP-1 assembly source to a 16-byte ROM image for Logisim Evolution.

Encoding: byte = (opcode << 4) | operand

Usage:
    python sap1_asm.py <program.asm>
    python sap1_asm.py <program.asm> --output <out.hex>

Syntax:
    ORG  <addr>        ; set current address (0-15, decimal/hex/binary)
    DATA <byte>        ; place raw 8-bit byte at current address
    LDA  <addr>        ; load memory → A
    LDB  <addr>        ; load memory → B
    STA  <addr>        ; store (A+B) → memory
    STS  <addr>        ; store (A-B) → memory
    ROR_A              ; rotate A right
    ROL_A              ; rotate A left
    ROR_B              ; rotate B right
    ROL_B              ; rotate B left
    JUMP <addr>        ; unconditional jump
    HLT                ; halt

    Comments: ; or #
    Operands: binary (e.g. 1110), decimal (14), or hex (E / 0xE)
    Labels:   LOOP:  (resolved on second pass)
"""

import sys
import argparse
import re

# ── Opcode table ──────────────────────────────────────────────────────────────
OPCODES = {
    "LDA":   (0x1, True),
    "LDB":   (0x2, True),
    "STA":   (0x3, True),
    "STS":   (0x4, True),
    "ROR_A": (0x6, False),
    "ROR_B": (0x7, False),
    "ROL_A": (0x8, False),
    "ROL_B": (0x9, False),
    "JUMP":  (0xA, True),
    "HLT":   (0xB, False),
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_int(token: str, labels: dict = None) -> int:
    """Parse an integer token (binary, hex, decimal) or a label name."""
    token = token.strip()
    if labels and token in labels:
        return labels[token]
    # binary: all 0/1 chars and length > 1 avoids single digit ambiguity
    if re.fullmatch(r'[01]+', token) and len(token) > 1:
        return int(token, 2)
    if token.startswith('0x') or token.startswith('0X'):
        return int(token, 16)
    if re.fullmatch(r'[0-9A-Fa-f]+', token):
        # Try decimal first; if it has hex chars, treat as hex
        if re.fullmatch(r'[0-9]+', token):
            return int(token, 10)
        return int(token, 16)
    raise ValueError(f"Cannot parse operand: '{token}'")


def strip_comment(line: str) -> str:
    for ch in (';', '#'):
        idx = line.find(ch)
        if idx != -1:
            line = line[:idx]
    return line.strip()


# ── Assembler ─────────────────────────────────────────────────────────────────

def assemble(source: str) -> list[int]:
    rom = [0x00] * 16
    lines = source.splitlines()

    # ── Pass 1: collect labels ────────────────────────────────────────────────
    labels: dict[str, int] = {}
    pc = 0
    for raw in lines:
        line = strip_comment(raw)
        if not line:
            continue
        # label definition
        if line.endswith(':'):
            labels[line[:-1].upper()] = pc
            continue
        tokens = line.upper().split()
        mnemonic = tokens[0]
        if mnemonic == 'ORG':
            pc = parse_int(tokens[1])
        elif mnemonic == 'DATA':
            pc += 1
        elif mnemonic in OPCODES:
            pc += 1
        # unknown directives silently skipped

    # ── Pass 2: emit bytes ────────────────────────────────────────────────────
    pc = 0
    errors = []
    for lineno, raw in enumerate(lines, 1):
        line = strip_comment(raw)
        if not line:
            continue
        if line.upper().endswith(':'):
            continue  # label, skip

        tokens = line.split()
        mnemonic = tokens[0].upper()

        try:
            if mnemonic == 'ORG':
                pc = parse_int(tokens[1], labels)
                if not (0 <= pc <= 15):
                    errors.append(f"Line {lineno}: ORG address {pc} out of range (0-15)")
            elif mnemonic == 'DATA':
                value = parse_int(tokens[1], labels) & 0xFF
                if not (0 <= pc <= 15):
                    errors.append(f"Line {lineno}: address {pc} out of range")
                else:
                    rom[pc] = value
                pc += 1
            elif mnemonic in OPCODES:
                opcode, has_operand = OPCODES[mnemonic]
                operand = 0
                if has_operand:
                    if len(tokens) < 2:
                        errors.append(f"Line {lineno}: {mnemonic} requires an operand")
                    else:
                        operand = parse_int(tokens[1], labels) & 0x0F
                if not (0 <= pc <= 15):
                    errors.append(f"Line {lineno}: address {pc} out of range")
                else:
                    rom[pc] = ((opcode & 0xF) << 4) | (operand & 0xF)
                pc += 1
            else:
                errors.append(f"Line {lineno}: unknown mnemonic '{mnemonic}'")
        except (ValueError, IndexError) as e:
            errors.append(f"Line {lineno}: {e}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    return rom


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SAP-1 Assembler — outputs a 16-byte Logisim ROM image"
    )
    parser.add_argument("source", help="Assembly source file (.asm)")
    parser.add_argument(
        "--output", "-o", default=None,
        help="Write hex output to file (default: print to stdout)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print annotated disassembly alongside hex"
    )
    args = parser.parse_args()

    with open(args.source, 'r') as f:
        source = f.read()

    rom = assemble(source)

    hex_line = " ".join(f"{b:02X}" for b in rom)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(hex_line + "\n")
        print(f"Written to {args.output}")
    else:
        print(hex_line)

    if args.verbose:
        print("\nAnnotated ROM:")
        for addr, byte in enumerate(rom):
            op  = (byte >> 4) & 0xF
            opd = byte & 0xF
            mnem = next((k for k, (v, _) in OPCODES.items() if v == op), "???")
            print(f"  0x{addr:X}: {byte:02X}  ({byte:08b})  {mnem} 0x{opd:X}")


if __name__ == "__main__":
    main()
