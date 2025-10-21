from .CompilationEngine import CompilationEngine
from .JackTokenizer import JackTokenizer
import sys
from pathlib import Path
import os
import writeToFile


def compile():
    """
    Handles user inputed file paths or folder paths for translating into xml.
    If no path is given, defaults to a pre-assigned path.
    """
    args = sys.argv
    default_path = "project10_tests/ArrayTest"
    # Determine user inputed file path or default file path.
    if len(args) < 2:
        print(f"No input path given, default: {default_path}")
        input_path = default_path
    else:
        input_path = args[1]
    if os.path.isdir(input_path):
        contents = []
        all_xml = []
        for file_name in os.listdir(input_path):
            if not file_name.endswith("Toutput.xml"):
                continue
            file_path = os.path.join(input_path, file_name)
            if os.path.isfile(file_path):
                ce = CompilationEngine()
                contents = writeToFile.parseFile(file_path)
                ce_xml, p10_xml = ce.compile(contents)
                all_xml += ce_xml
                p10_output = Path(file_name).stem + "p10output.xml"
                output_file = Path(file_name).stem + "_TCEoutput.vm"
                main_xml_file = os.path.join(input_path, output_file)
                p10_xml_file = os.path.join(input_path, p10_output)
                writeToFile.outToFolder(p10_xml_file, p10_xml, change=False)
                writeToFile.outToFolder(main_xml_file, ce_xml, change=False)
        all_main_xml_file = os.path.join(input_path, os.path.basename(os.path.normpath(input_path)) + ".vm")
        writeToFile.outToFolder(all_main_xml_file, all_xml, change=False)
        print(f"{all_main_xml_file} created.")

    else:
        raise Exception("no path.")
    return


def tokenize():
    """
    Handles user inputed file paths or folder paths for translating into xml.
    If no path is given, defaults to a pre-assigned path.
    """
    args = sys.argv
    default_path = "project10_tests/ArrayTest"
    # Determine user inputed file path or default file path.
    if len(args) < 2:
        print(f"No input path given, default: {default_path}")
        input_path = default_path
    else:
        input_path = args[1]
    tokenizer = JackTokenizer()
    if os.path.isdir(input_path):
        contents = []
        for file_name in os.listdir(input_path):
            if not file_name.endswith(".jack"):
                continue
            file_path = os.path.join(input_path, file_name)
            if os.path.isfile(file_path):
                contents = writeToFile.parseFile(file_path)
                xml_lines = tokenizer.tokenize(contents)
                output_file = Path(file_name).stem + "_Toutput.xml"
                main_xml_file = os.path.join(input_path, output_file)
                writeToFile.outToFolder(main_xml_file, xml_lines, change=False)
    else:
        raise Exception("no path.")
    return



if __name__ == "__main__":
    tokenize()
    compile()