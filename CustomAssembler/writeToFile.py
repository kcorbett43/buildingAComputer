# Clean user provided file.
#
# Author: Kevin Corbett
# Version: 1.1
# File Name: writeToFile.py
# Date: 10/28/2024


import sys


def parseAsm(input_path):
    """
    Takes in a user inputed file path with a ".asm" file extension and 
    creates a list of the lines in the file striped leading white 
    space and comments.

    Input:
        input_path [str] - A file path with the extension .asm

    Output:
        Creates a list of the contents of the input_path with 
        the leading white space and comments removed.
    """
    input_file_contents = []
    # Open file and clean its contents.
    with open(input_path, 'r') as file:
        lines = file.readlines()
        input_file_contents = cleanLines(lines)
    
    # Check if there is a new line at the end of the file and remove it.
    last_line = input_file_contents[-1]
    input_file_contents[-1] = last_line.rstrip('\n')

    # Write updated content to the output path.
    #input_file_contents = ''.join(input_file_contents)
    return input_file_contents


def outToFolder(output_path, contents):
    """
    Takes in a user inputed file path with a ".asm" file extension and 
    creates a file in the same directory with the ".hack" extension

    Input:
        output_path [str] - A file path with the extension .asm
        contents [list] - List of the contents to output to the file

    Output:
        Creates a file with the contents of the contents in the path 
        provided by output_path
    """
    # Set input and output file paths
    # but with the ".hack" extension
    output_path = output_path[:-4] + ".hack"
    output_file = open(output_path, "w")
    contents = '\n'.join(contents)
    output_file.write(contents)


def cleanLines(lines):
    """
    Removes comments and whitespace from a list of lines of code.

    Inputs:

        contents: list[str] - the list of lines of code.

    Returns:

        Returns code with out whitespace or comments.
    """
    clean_lines = []

    i = 0
    # Loop through each line of code and remove comments and whitespace.
    while i < len(lines):
        line = lines[i]
        line = cleanFileLine(line)

        comment_index = line.find("//")
        if comment_index != -1:
            line = line[:comment_index]
        line = cleanFileLine(line)

        # Remove multiline comment if it is on a single line.
        # E.g. code... /* ... comments ... */
        if "/*" in line and "*/" in line:
            begin_index = line.index("/*")
            end_index = line.index("*/")
            begin_line = line[0:begin_index]
            end_line = line[end_index+2:]
            line = begin_line + end_line

        line = cleanFileLine(line)

        if line is None or line == "":
            i += 1
            continue
        clean_lines.append(line)

        # Remove lines of code if it is in a multiline comment.
        if "/*" in line:
            comment_index = line.index("/*")
            line = line[:comment_index]
            line = cleanFileLine(line)
            cleanFileLine(line)
            i += 1
            while "*/" not in line and i < len(lines):
                i += 1     
        i += 1
    return clean_lines
                

def cleanFileLine(line):
    """
    Removes whitespace and new lines from a line of code.

    Inputs:

        line: str - The line of code.

    Returns:

        Returns line of code with whitespace and newlines removed.
    """

    line = line.strip()
    line = line.replace("/n", "")
    return line