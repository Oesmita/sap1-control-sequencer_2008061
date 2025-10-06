# sap1-control-sequencer_2008061
# SAP-1 Control Sequencer (Logisim-Evolution)

> A fully automatic SAP-1 CPU with hardwired control sequencer, RAM auto-loader, and a Python assembler.  
> **Unique feature:** unconditional `JUMP`.  
> **Arithmetic-on-store semantics:** `STA addr` stores **A + B** → `M[addr]`, `STS addr` stores **A − B** → `M[addr]`.

---

## 🔗 Quick Links
- **GitHub Release:** https://github.com/<your-user>/<sap1-project>/releases/tag/v1.0.0
- **YouTube Demo (2–4 min):** https://youtu.be/<your-video-id>
- **Final Report:** `docs/Final_Report_SAP1_Control_Sequencer.md` (or link if PDF)
- **Commit used in video:** `<abc1234>`

---

## Table of Contents
1. [Overview](#overview)
2. [Repository Layout](#repository-layout)
3. [Architecture](#architecture)
4. [Instruction Set (ISA)](#instruction-set-isa)
5. [Micro-Timing (T-states)](#micro-timing-t-states)
6. [Assembly Language & File Formats](#assembly-language--file-formats)
7. [Quick Start](#quick-start)
8. [Sample Programs](#sample-programs)
9. [Run in Logisim-Evolution](#run-in-logisim-evolution)
10. [Verification & Expected Results](#verification--expected-results)
11. [Reproducibility](#reproducibility)
12. [License](#license)
13. [Acknowledgments](#acknowledgments)

---

## Overview
This project implements a SAP-1-style microprocessor in **Logisim-Evolution** with:
- A **hardwired control sequencer** (T-state ring counter + opcode decode),
- A **RAM auto-loader** workflow for fast program loading,
- A **Python assembler** tailored to the ISA,
- A detailed **report** so another student can rebuild the machine from scratch.

**Design choices**: single shared bus, 8-bit data, 4-bit address (16 bytes). Arithmetic is performed only when storing to memory: `STA` = A+B, `STS` = A−B.

---

## Repository Layout
