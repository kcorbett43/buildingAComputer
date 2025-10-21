# Translate VM code to assembly.
#
# Author: Kevin Corbett
# Version: 1.1
# File Name: hackVirtualMachine.py
# Date: 11/11/2024


import writeToFile
import sys
from pathlib import Path
import os


class VirtualMachine:


    # Beginning address of temp
    temp_address = 5


    def __init__(self, file=None):
        """
        Initializes the virtual machine with:
            var_counter: [int] - Used to create unique variable names.
            file: [str] -  Used to create unique variable names.
            cur_function [str] - Used to define the scope when calling 
                a function.
        """
        self.var_counter = 0
        if file:
            self.file = file.replace("/", "_")
            self.cur_function = self.file
        else:
            self.file = None
            self.cur_function = None


    def set_filepath(self, file):
        """
        Sets the file being translated and initial current function.

        Inputs:

            file: [str] - 
        """
        self.file = file.replace("/", "_")
        self.cur_function = self.file
        return None


    def translate(self, contents):
        """
        Translates code to asm.

        Inputs:

            contents: list[str] - a list of the lines of code.

        Returns:

            Returns the translated code in asm.
        """
        asm_lines = []#self._call(["call", "Sys.init", "0"])

        # For each code line in contents, get the equivalent asm code.
        for line in contents:
            line = line.split()
            if line[0] == "push":
                asm_lines += self._push(line[1:])
            elif line[0] == "pop":
                asm_lines += self._pop(line[1:])
            elif line[0] == "add" or line[0] == "sub":
                asm_lines += self._addSub(line[0])
            elif line[0] == "gt" or line[0] == "lt" or line[0] == "eq":
                asm_lines += self._comparisons(line[0])
            elif line[0] == "neg":
                asm_lines += self._neg()
            elif line[0] == "or":
                asm_lines += self._or()
            elif line[0] == "not":
                asm_lines += self._not()
            elif line[0] == "and":
                asm_lines += self._and()
            elif line[0] == "label":
                asm_lines += self._label(line[1])
            elif line[0] == "if-goto":
                asm_lines += self._ifGoto(line[1])
            elif line[0] == "goto":
                asm_lines += self._goto(line[1])
            elif line[0] == "function":
                asm_lines += self._functionDef(line)
            elif line[0] == "return":
                asm_lines += self._return()
            elif line[0] == "call":
                asm_lines += self._call(line)
        return asm_lines
    

    def _bootstrapCode(self):
        """
        Initializes the Stack Pointer.
        """
        asm_lines = [
            "// Set SP to 256",
            "@256", 
            "D=A",
            "@SP",
            "M=D"
        ]
        return asm_lines


    def _call(self, line):
        """
        Translates vm function call to asm.

        Inputs:

            contents: line - line of code defining the function call.

        Returns:

            Returns the translated function call.
        """
        func_name = line[1] 
        if len(line) > 2:
            num_vars = int(line[2])
        else:
            num_vars = 0
        return_address = self._createReturnAddress(self.cur_function)
        
        # push return address
        asm_lines = [
            f"//   call: {' '.join(line)}",
            "// push return address",
            f"@{return_address}",
            "D=A",
            "@SP",
            "AM=M+1",
            "A=A-1",
            "M=D"
        ]

        push_sequence = [
            "D=M",
            "@SP",
            "AM=M+1",
            "A=A-1",
            "M=D"
        ]

        # push LCL
        asm_lines += [
            "// push LCL",
            "@LCL"
        ]
        asm_lines += push_sequence

        # push ARG
        asm_lines += [
            "// push ARG",
            "@ARG"
        ]
        asm_lines += push_sequence

        # push THIS
        asm_lines += [
            "// push this",
            "@THIS"
        ]
        asm_lines += push_sequence

        # push THAT
        asm_lines += [
            "// push THAT",
            "@THAT"
        ]
        asm_lines += push_sequence

        # ARG = SP - n - 5
        asm_lines += [
            "// ARG = SP - n - 5",
            "@SP",
            "D=M",
            f"@{num_vars + 5}",
            "D=D-A",
            "@ARG",
            "M=D"
        ]

        # LCL = SP
        asm_lines += [
            "// LCL = SP",
            "@SP",
            "D=M",
            "@LCL",
            "M=D",
            f"// goto {func_name}",
            f"@{func_name}",
            "0;JMP",
            f"// return address label: {return_address}",
            f"({return_address})"
        ]

        return asm_lines


    def _return(self):
        """
        Translates vm return function to asm.

        Inputs:

            contents: line - line of code defining the return function.

        Returns:

            Returns the translated return function.
        """
        asm_lines = ["//   return"]

        # FRAME = LCL
        asm_lines += [
            "// FRAME = LCL",
            "@LCL",
            "D=M",
            "@FRAME",
            "M=D"
        ]

        # RET = *(FRAME - 5)
        asm_lines += [
            "// RET = *(FRAME - 5)",
            "@FRAME",
            "D=M",
            f"@{self.temp_address}",
            "A=D-A",
            "D=M",
            "@RET",
            "M=D"
        ]

        # *ARG = pop()
        asm_lines += [
            "// *ARG = pop()",
            "@SP",
            "AM=M-1",
            "D=M",
            "@ARG",
            "A=M",
            "M=D"
        ]

        # SP = ARG + 1
        asm_lines += [
            "// SP = ARG + 1",
            "@ARG",
            "D=M+1",
            "@SP",
            "M=D"
        ]

        # THAT = *(FRAME - 1)
        asm_lines += [
            "// THAT = *(FRAME - 1)",
            "@FRAME",
            "A=M-1",
            "D=M",
            "@THAT",
            "M=D"
        ]

        # THIS = *(FRAME - 2)
        asm_lines += [
            "// THIS = *(FRAME - 2)",
            "@FRAME",
            "D=M-1",
            "A=D-1",
            "D=M",
            "@THIS",
            "M=D"
        ]

        # ARG = *(FRAME - 3)
        asm_lines += [
            "// ARG = *(FRAME - 3)",
            "@FRAME",
            "D=M-1",
            "D=D-1",
            "A=D-1",
            "D=M",
            "@ARG",
            "M=D"
        ]

        # LCL = *(FRAME - 4)
        asm_lines += [
            "// LCL = *(FRAME - 4)",
            "@FRAME",
            "D=M",
            "@4",
            "A=D-A",
            "D=M",
            "@LCL",
            "M=D"
        ]

        # goto RET
        asm_lines += [
            "// goto RET",
            "@RET",
            "A=M",
            "0;JMP"
        ]

        return asm_lines


    def _functionDef(self, line):
        """
        Translates vm function definition to asm.

        Inputs:

            contents: line - line of code defining the vm function definition.

        Returns:

            Returns the translated function definition.
        """
        func_name = line[1]
        # Tells the VM what the current function being translated is.
        # Used primarily for specifying the return address when calling a
        # different function. See _call.
        self.cur_function = func_name
        if len(line) > 2:
            num_vars = int(line[2])
        else:
            num_vars = 0
        
        asm_lines = [
            f"// function definition for {' '.join(line)}",
            f"({func_name})",
            "@SP"
        ]

        # Create space for local variables.
        if num_vars > 0:
            asm_lines.append("A=M")
            asm_lines.append("M=0")
            while num_vars - 1 > 0:
                asm_lines.append("A=A+1")
                asm_lines.append("M=0")
                num_vars -= 1
            asm_lines += [
                "D=A+1",
                "@SP",
                "M=D"
            ]

        return asm_lines


    def _ifGoto(self, line):
        """
        Translates vm if-goto command to asm.

        Inputs:

            contents: line - line of code defining the vm if-goto command.

        Returns:

            Returns the translated if-goto command.
        """
        asm_lines = [
            f"// if-goto {line}",
            "@SP",
            "AM=M-1",
            "D=M",  
            f"@{line}",
            "D;JNE"
        ]
        return asm_lines
    

    def _goto(self, line):
        """
        Translates vm goto command to asm.

        Inputs:

            contents: line - line of code defining the vm goto command.

        Returns:

            Returns the translated goto command.
        """
        asm_lines = [
            f"// GOTO {line}",
            f"@{line}",
            "0;JMP"
        ]
        return asm_lines


    def _label(self, line):
        """
        Adds label to asm.

        Inputs:

            contents: line - label to add.

        Returns:

            Returns the label.
        """
        asm_lines = [
            f"// add label: {line}",
            f"({line})"
        ]
        return asm_lines


    def _pop(self, line):
        """
        Translates pop commands to the appropriate assembly code.

        Inputs:

            line: list[str] - vm pop command.

        Returns:

            Returns the translated pop command in asm.
        """
        segment = line[0]
        address = int(line[1])
        asm_lines = [f"// pop {segment} {address}"]

        # Set pointer address to THIS or THAT.
        if segment == "pointer":
            if address == 0:
                address = "THIS"
            elif address == 1:
                address = "THAT"

        if segment == "argument" or segment == "local" or \
            segment == "this" or segment == "that":
            # each of these segments contain a memory address that 
            # points to the start of their place in memory.
            if segment == "argument":
                asm_lines.append("@ARG")
            elif segment == "local":
                asm_lines.append("@LCL")
            elif segment == "this":
                asm_lines.append("@THIS")
            elif segment == "that":
                asm_lines.append("@THAT")
            # Logic to get to the correct memory location and 
            # update their value.
            asm_lines.append("D=M")
            asm_lines.append(f"@{address}")
            asm_lines.append("D=D+A")
            asm_lines.append("@R13")

            asm_lines.append("M=D")
            asm_lines.append("@SP")
            asm_lines.append("AM=M-1")
            asm_lines.append("D=M")
            asm_lines.append("@R13")
            asm_lines.append("A=M")
            asm_lines.append("M=D")
        elif segment == "temp" or segment == "static" or segment == "pointer":
            # Each of these segments directly contain their values.
            if segment == "temp":
                address += self.temp_address
            elif segment == "static":
                address = self._getVarName(address)
            asm_lines.append("@SP")
            asm_lines.append("AM=M-1")
            asm_lines.append("D=M")
            asm_lines.append(f"@{address}")
            asm_lines.append("M=D")

        return asm_lines


    def _push(self, line):
        """
        Translates push commands to the appropriate assembly code.

        Inputs:

            line: list[str] - vm push command.

        Returns:

            Returns the translated push command in asm.
        """
        asm_lines = []
        segment = line[0]
        address = int(line[1])
        asm_lines.append(f"// push {segment} {address}")

        if segment == "constant":
            # Add the address to the stack.
            asm_lines.append(f"@{address}")
            asm_lines.append("D=A")
            asm_lines.append("@SP")
            asm_lines.append("A=M")
            asm_lines.append("M=D")
            asm_lines.append("@SP")
            asm_lines.append("M=M+1")
        else:
            # For each of these segments, their location in memory must be
            # found before pushing their value to the stack.
            if segment == "local" or segment == "that" or \
                segment == "this" or segment == "argument":
                # local, that, etc need to have their address dereferenced.
                if segment == "local":
                    asm_lines.append("@LCL")
                elif segment == "that":
                    asm_lines.append("@THAT")
                elif segment == "this":
                    asm_lines.append("@THIS")
                elif segment == "argument":
                    asm_lines.append("@ARG")
                asm_lines.append("D=M")
                asm_lines.append(f"@{address}")
                asm_lines.append("A=D+A")
            # temp, static, etc can have their address computed directly.
            elif segment == "temp":
                address += self.temp_address
                asm_lines.append(f"@{address}")
            elif segment == "static":
                address = self._getVarName(address)
                asm_lines.append(f"@{address}")
            elif segment == "pointer":
                if address == 0:
                    asm_lines.append("@THIS")
                elif address == 1:
                    asm_lines.append("@THAT")

            asm_lines.append("D=M")
            asm_lines.append("@SP")
            asm_lines.append("AM=M+1")
            asm_lines.append("A=A-1")
            asm_lines.append("M=D")
        
        return asm_lines

    
    def _addSub(self, add_or_sub):
        """
        Translates an add or sub command to the appropriate assembly code.

        Inputs:

            add_or_sub: str - determines whether the command is add or sub.

        Returns:

            Returns the translated add or sub command in asm.
        """
        asm_lines = [f"// {add_or_sub}"]

        asm_lines.append("@SP") 
        asm_lines.append("AM=M-1") 
        asm_lines.append("D=M") 
        asm_lines.append("A=A-1") 
        if add_or_sub == "add":
            asm_lines.append("M=D+M") 
        else:
            asm_lines.append("M=M-D")

        return asm_lines


    def _neg(self):
        """
        Translates a neg command to the appropriate assembly code.

        Returns:

            Returns the translated neg command in asm.
        """
        asm_lines = ["// neg"]

        asm_lines.append("@SP") 
        asm_lines.append("A=M-1") 
        asm_lines.append("M=-M")

        return asm_lines
    

    def _not(self):
        """
        Translates a not command to the appropriate assembly code.

        Returns:

            Returns the translated not command in asm.
        """
        asm_lines = ["// not"]

        asm_lines.append("@SP")
        asm_lines.append("A=M-1")
        asm_lines.append("M=!M")

        return asm_lines
    

    def _or(self):
        """
        Translates an or command to the appropriate assembly code.

        Returns:

            Returns the translated or command in asm.
        """
        asm_lines = ["// or"]

        asm_lines.append("@SP")
        asm_lines.append("AM=M-1")
        asm_lines.append("D=M")
        asm_lines.append("A=A-1")
        asm_lines.append("M=D|M")

        return asm_lines


    def _and(self):
        """
        Translates an and command to the appropriate assembly code.

        Returns:

            Returns the translated and command in asm.
        """
        asm_lines = ["// and"]

        asm_lines.append("@SP")
        asm_lines.append("AM=M-1")
        asm_lines.append("D=M")
        asm_lines.append("A=A-1")
        asm_lines.append("M=D&M")

        return asm_lines


    def _comparisons(self, comparison):
        """
        Translates a comparison command (gt, lt, eq) to the appropriate 
        assembly code.

        Returns:

            Returns the translated comparison command in asm.
        """
        asm_lines = [f"// {comparison}"]
        # Assume comparison is true, if it ends up being false, update
        # the return value.
        asm_lines.append("@SP")
        asm_lines.append("AM=M-1")
        asm_lines.append("D=M")
        asm_lines.append("A=A-1")
        asm_lines.append("D=M-D")       # LARGE POSITIVE IF NEGATIVE
        asm_lines.append("M=-1") # -1 is True
        continue_var = self._createVarName("CONTINUE")
        asm_lines.append(f"@{continue_var}")
        # Determine jump if it is true.
        if comparison == "gt":
            asm_lines.append("D;JGT")
        elif comparison == "lt":
            asm_lines.append("D;JLT")
        elif comparison == "eq":
            asm_lines.append("D;JEQ")
        # If no jump, set to 0 (False)
        asm_lines.append("@SP")
        asm_lines.append("A=M-1")
        asm_lines.append("M=0")
        asm_lines.append(f"({continue_var})")
        return asm_lines
        

    def _createVarName(self, name):
        """
        Creates a unique variable name using the file name and the
        variable counter.

        Inputs:

            name: str - Provided variable name. 

        Returns:

            Returns the provided name appended with the file name and
            the variable counter.
        """
        self.var_counter += 1
        return f"{name}.{self.file}.{self.var_counter}"
    

    def _createReturnAddress(self, name):
        """
        Creates a unique variable name using the name provided and the
        variable counter.

        Inputs:

            name: str - Provided variable name. 

        Returns:

            Returns the provided name appended with the name provided and
            the variable counter.
        """
        self.var_counter += 1
        return f"{name}.{self.var_counter}"
    

    def _getVarName(self, counter):
        """
        Gets a specific variable in the form file_name.counter. Primarily
        used for static variables.

        Inputs:

            counter: int - Index specifying which variable to produce. 

        Returns:

            Returns the variable name corresponding the the counter.
        """
        return f"{self.file}.{counter}"




def main():
    """
    Handles user inputed file paths or folder paths for translating into asm.
    If no path is given, defaults to a pre-assigned path.
    """
    args = sys.argv
    default_path = "src/vmAndAsmFiles/SimpleAdd.vm"
    # Determine user inputed file path or default file path.
    if len(args) < 2:
        print(f"No input path given, default: {default_path}")
        input_path = default_path
    else:
        input_path = args[1]
    vm = VirtualMachine()
    asm_lines = vm._bootstrapCode()
    asm_lines += vm._call(["call", "Sys.init", "0"])

    if os.path.isdir(input_path):
        contents = []
        for file_name in os.listdir(input_path):
            if not file_name.endswith(".vm"):
                continue
            file_path = os.path.join(input_path, file_name)
            if os.path.isfile(file_path):
                contents = writeToFile.parseFile(file_path)
                vm.set_filepath(file_path)
                asm_lines += vm.translate(contents)
        output_file = Path(input_path).name + ".asm"
        main_asm_file = os.path.join(input_path, output_file)
        writeToFile.outToFolder(main_asm_file, asm_lines, change=False)
        print(f"{main_asm_file} created")
    else:
        contents = writeToFile.parseFile(input_path)
        # Initialize assembler and translate code.
        file_name = Path(input_path).stem
        vm = VirtualMachine(file_name)
        asm_lines = vm.translate(contents)
        writeToFile.outToFolder(input_path, asm_lines)
        print(f"{input_path[:-2]}asm created")
    return


if __name__ == "__main__":
    main()