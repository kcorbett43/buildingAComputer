# Building a Computer 
An end-to-end implementation of the Hack Computer, built from the ground up following the Nand to Tetris course (https://www.nand2tetris.org/).

---

## Overview  
This repository reconstructs the Hack computer system and its entire software stack.  
Starting from a virtualized hardware architecture, it layers on an assembler, compiler, and high-level language, ultimately producing a game that runs on your own simulated machine.

It’s an exploration of how computers actually work, mirroring the design process from the Nand to Tetris course.

---


---

### `CustomVirtualMachine/`
Implements the Hack CPU and memory model in software — the base “hardware” layer of the computer.  
It defines:
- The instruction set architecture (ISA) used by Hack assembly  
- The memory segments, stack operations, and arithmetic logic unit (ALU)  
- A runtime capable of executing `.hack` machine code  

> This is effectively your own working computer, simulated in code.

---

### `CustomAssembler/`
Converts Hack Assembly (`.asm`) programs into binary machine code understood by the Hack Virtual Machine.  
It handles:
- Parsing instructions and symbolic labels  
- Translating mnemonic operations into 16-bit binary words  
- Producing `.hack` executable files  

This module bridges the human-readable assembly to machine’s binary logic.

---

### `CustomCompiler/`
Implements a compiler for a high-level Hack language, similar to the Jack language in Nand to Tetris.  
It performs:
- Lexical and syntactic analysis of the source language  
- Code generation into Hack VM code or assembly  
- Optional optimizations and error reporting 

---

### `Game/`
Contains a working game written in the Hack-language.  
It demonstrates:
- Full integration of the compiler, assembler, and VM  
- Execution of compiled code on the Hack architecture  
- Visual or text-based output, depending on the implementation  

---

### Acknowledgements
This was built during the Introduction to Computer Systems course at UChicago.

