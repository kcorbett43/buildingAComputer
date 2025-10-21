# Translate code to binary.
#
# Author: Kevin Corbett
# Version: 1.0
# File Name: hackAssembler.py
# Date: 10/28/2024


import writeToFile
import sys


class Assembler:

    def __init__(self):
        """
        Initializes the assembler with:
            cur_var_address: [int] - start memory address for new variables
            null_dest: [str] - place in the symbol table for null destinations.
            null_jump: [str] - place in the symbol table for null jumps.
            symbol_table [dict] - keeps track of symbols.
        """
        self.cur_var_address = 16
        self.null_dest = "nullDest"
        self.null_jump = "nullJump"
        self.symbol_table = {
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "R0": 0,
            "R1": 1,
            "R2": 2,
            "R3": 3,
            "R4": 4,
            "R5": 5,
            "R6": 6,
            "R7": 7,
            "R8": 8,
            "R9": 9,
            "R10": 10,
            "R11": 11,
            "R12": 12,
            "R13": 13,
            "R14": 14,
            "R15": 15,
            "SCREEN": 16384,
            "KBD": 24576, 
            # Start of comp a=0
            "0": "101010",
            "1": "111111",
            "-1": "111010",
            "D": "001100",
            "A": "110000",
            "!D": "001101",
            "!A": "110001",
            "-D": "001111",
            "-A": "110011",
            "D+1": "011111",
            "A+1": "110111",
            "D-1": "001110",
            "A-1": "110010",
            "D+A": "000010",
            "D-A": "010011",
            "A-D": "010011",
            "D&A": "000000",
            "D|A": "010101",
            # Start of comp= a=1
            "M": "110000",
            "!M": "110001",
            "-M": "110011",
            "M+1": "110111",
            "M-1": "110010",
            "D+M": "000010",
            "D-M": "010011",
            "M-D": "000111",
            "D&M": "000000",
            "D|M": "010101",
            # Start of dest
            "dnullDest": "000", # Value is not stored
            "dM": "001",
            "dD": "010", 
            "dMD": "011",
            "dA": "100",
            "dAM": "101",
            "dAD": "110",
            "dAMD": "111",
            # Start of jump
            "nullJump": "000",
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111"
        }


    def translate(self, contents):
        """
        Translates code to binary.

        Inputs:

            contents: list[str] - a list of the lines of code.

        Returns:

            Returns the translated code in binary.
        """
        binary_lines = []
        contents = self._firstPass(contents)
        line_number = 0
        for line in contents:
            is_a_instruction = line[0]
            # Determine if line is an A or C instruction and translate.
            if is_a_instruction == "@":
                line = self._translateA(line)
            else:
                line = self._translateC(line)
            binary_lines.append(line)
            line_number += 1 
        return binary_lines       


    def _firstPass(self, contents):
        """
        The first pass of the assembler. Adds labels to the symbol table and
        removes them from the list of code instructions.

        Inputs:

            contents: list[str] - List of lines of code.

        Returns:

            The lines of code with the labels removed.
        """
        i = 0
        while i < len(contents):
            line = contents[i]
            if line[0] == "(":
                # Add label to the symbol table and continue. 
                # Do not increment line number.
                # Increment current variable address
                self._addLabelToSymbolTable(line, i)
                contents.pop(i)
                continue
            i += 1
        return contents


    def _addLabelToSymbolTable(self, line, line_number):
        """
        Adds a label to the symbol table with the corresponding line number.

        Inputs:

            line: str - the line of code with the label.
            line_number: int - the line number of the label.
        """
        # Remove enclosing parenthesis
        label = line[1:len(line)-1]
        self.symbol_table[label] = line_number
        return 


    def _translateA(self, line):
        """
        Translates an A instruction to binary

        Inputs:

            line: str - the A instruction.

        Returns:

            Returns the binary A instruction.
        """
        # Remove the leading "@" symbol and convert to binary
        a = line[1:]
        if a.isdigit():
            # If the A instruction is a digit, convert to binary.
            a = f"{int(a):016b}"
        elif not a.isdigit():
            # If the A instruction is a symbol, get from symbol table
            # or add it to the symbol table with the correct address.
            if a in self.symbol_table.keys():
                a = self.symbol_table[a]
                if type(a) == int:
                    a = f"{int(a):016b}"
            else:
                self.symbol_table[a] = self.cur_var_address
                self.cur_var_address += 1
                a = self.symbol_table[a]
                if type(a) == int:
                    a = f"{int(a):016b}"

        return a


    def _translateC(self, line):
        """
        Translates C instruction to binary.

        Inputs:

            line: str - the C instruction.

        Returns:

            Returns the binary C instruction.
        """
        # C instructions begin with 111.
        c = "111"

        # Find the destination.
        if "=" in line:
            equal_index = line.index("=")
            dest = line[0:equal_index]
            assignment = line[equal_index+1:]
        else:
            dest = self.null_dest
            assignment = line 
        
        # Find comp and jump
        if ";" in assignment:
            semi_index = assignment.index(";")
            comp = assignment[0:semi_index]
            jump = assignment[semi_index+1:]
        else:
            comp = assignment
            jump = self.null_jump

        # Set a-bit
        if "M" in comp:
            c += "1"
        else:
            c += "0"

        # Translate dest, comp and jump into binary
        c += self._translateComp(comp)
        c += self._translateDest(dest)
        c += self._translateJump(jump)

        return c


    def _translateDest(self, dest):
        """
        Translates the destination of an instruction to binary.

        Inputs:

            dest: str - the destination of a C instruction.

        Returns:

            Returns the binary destination of a C instruction.
        """
        return self.symbol_table[f"d{dest}"]


    def _translateJump(self, jump):
        """
        Translates the jump of an instruction to binary.

        Inputs:

            jump: str - the jump of a C instruction.

        Returns:

            Returns the binary jump of a C instruction.
        """
        return self.symbol_table[jump]


    def _translateComp(self, comp):
        """
        Translates the computation of an instruction to binary.

        Inputs:

            comp: str - the computation of the C instruction

        Returns:

            Returns the binary computation of a C instruction.
        """
        return self.symbol_table[comp]


def main():
    """
    Handles user inputed file paths for translating into binary.
    If not path is given, defaults to a pre-assigned path.
    """
    args = sys.argv
    default_path = "src/asmAndHackFiles/PongL.asm"
    # Determine user inputed file path or default file path.
    if len(args) < 2:
        print(f"No input path given, default: {default_path}")
        input_path = default_path
    else:
        input_path = args[1]
    contents = writeToFile.parseAsm(input_path)
    # Initialize assembler and translate code.
    assembler = Assembler()
    binary_lines = assembler.translate(contents)
    writeToFile.outToFolder(input_path, binary_lines)
    print(f"{input_path[:-3]}hack created")
    return 


if __name__ == "__main__":
    main()