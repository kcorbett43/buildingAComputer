import re
import sys
from pathlib import Path
import os
import writeToFile

class CompilationEngine:


    def __init__(self):
        '''
        Initializes engine with regular expressions.
        '''
        self._token_re()


    def _token_re(self):
        '''
        Initializes relevant regular expressions for compiling a Jack program.
        '''
        self.keyword_pattern = r'\b(?:class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)\b'
        self.symbol_pattern = r'[\{\}\(\)\[\]\.\,\;\+\-\*\/&\|<>=~]'
        self.integer_constant_pattern = r'\b(?:0|[1-9][0-9]{0,4})\b'
        self.string_constant_pattern = r'[^"\n]*'
        self.identifier_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        self.token_pattern = f'{self.keyword_pattern}|{self.integer_constant_pattern}|{self.string_constant_pattern}'
        self.opterms = r"(\+|\-|\*|\/|\&|\||\<|\>|\=|\-|\~)"
        self.unary = r"(\-|\~)"
        self.class_symbols = {"this": 0, "static": 0, "local": 0, "arg": 0}
        self.method_symbols = {"this": 0, "static": 0, "local": 0, "arg": 0}
        self.method_table = {}
        self.class_table = {}
        self.new_compiled = []
        self.cur_class = None
        self.label_counter = 0
        self.method_names = set()
        self.char_dict = {
            ' ': 32, '!': 33, '"': 34, '#': 35, '$': 36, '%': 37, '&': 38, "'": 39,
            '(': 40, ')': 41, '*': 42, '+': 43, ',': 44, '-': 45, '.': 46, '/': 92,
            '0': 48, '1': 49, '2': 50, '3': 51, '4': 52, '5': 53, '6': 54, '7': 55,
            '8': 56, '9': 57, ':': 58, ';': 59, '<': 60, '=': 61, '>': 62, '?': 63,
            '@': 64, 'A': 65, 'B': 66, 'C': 67, 'D': 68, 'E': 69, 'F': 70, 'G': 71,
            'H': 72, 'I': 73, 'J': 74, 'K': 75, 'L': 76, 'M': 77, 'N': 78, 'O': 79,
            'P': 80, 'Q': 81, 'R': 82, 'S': 83, 'T': 84, 'U': 85, 'V': 86, 'W': 87,
            'X': 88, 'Y': 89, 'Z': 90, '[': 91, ']': 93, '^': 94, '_': 95, '`': 96,
            'a': 97, 'b': 98, 'c': 99, 'd': 100, 'e': 101, 'f': 102, 'g': 103, 
            'h': 104, 'i': 105, 'j': 106, 'k': 107, 'l': 108, 'm': 109, 'n': 110,
            'o': 111, 'p': 112, 'q': 113, 'r': 114, 's': 115, 't': 116, 'u': 117,
            'v': 118, 'w': 119, 'x': 120, 'y': 121, 'z': 122, '{': 123, '|': 124,
            '}': 125, '~': 126, 'DEL': 127, '\n': 128, 'backSpace': 129,
            'leftArrow': 130, 'upArrow': 131, 'rightArrow': 132, 'downArrow': 133,
            'home': 134, 'end': 135, 'pageUp': 136, 'pageDown': 137, 'insert': 138,
            'delete': 139, 'esc': 140, 'f1': 141, 'f2': 142, 'f3': 143, 'f4': 144,
            'f5': 145, 'f6': 146, 'f7': 147, 'f8': 148, 'f9': 149, 'f10': 150,
            'f11': 151, 'f12': 152
        }




    def compile(self, contents):
        '''
        Main compilation loop.
        '''
        contents = self.parse_xml(contents)
        compiled_code = []
        i = 0
        while i < len(contents):
            line = contents[i]
            tag = line.tag
            content = line.content
            if tag == "keyword" and content == "class":
                compiled_code += ["<class>"]
                class_code, i = self.compileClass(contents, i)
                compiled_code += class_code
                compiled_code += ["</class>"]
            i += 1
        compiled_code = BaseXML.many_to_str(compiled_code)
        return self.new_compiled, compiled_code
               

    def create_label(self):
        label = f"{self.cur_class}_{self.label_counter}"
        self.label_counter += 1
        return label
    
    def _reset_symbols(self, is_class):
        if is_class:
            self.class_symbols = {"this": 0, "static": 0, "local": 0, "arg": 0}    
            self.class_table = {}
        else:
            self.method_symbols = {"this": 0, "static": 0, "local": 0, "arg": 0}
            self.method_table = {}

    def compileClass(self, contents, i):
        '''
        Compiles a Jack class.
        '''
        self._reset_symbols(True)

        # class
        self.cur_class = contents[i+1].content
        class_code = contents[i:i+3]
        i += 3

        # Get method names
        m_index = i
        while m_index < len(contents):
            if contents[m_index].content == "method":
                self.method_names.add(contents[m_index+2].content)
            m_index += 1
        # classVarDec
        while (i < len(contents)) and ( contents[i].is_keyword() and ( contents[i].content_is(["static", "field"]) ) ):
            class_code += ["<classVarDec>"]
            while i < len(contents) and contents[i].content != ";":
                if contents[i].content in ["field", "static"]:
                    kind = contents[i].content
                    if kind == "field":
                        kind = "this"
                    cur_type = contents[i+1].content
                    self.class_table[f"{contents[i+2].content}"] = { "num": self.method_symbols[kind], "kind": kind, "type": cur_type }
                    self.method_symbols[kind] += 1
                elif contents[i-1].content == ",":
                    self.class_table[f"{contents[i].content}"] = { "num": self.method_symbols[kind], "kind": kind, "type": cur_type }
                    self.method_symbols[kind] += 1

                class_code += [contents[i]]
                i += 1
            class_code += [contents[i]] # ";"
            class_code += ["</classVarDec>"]
            i += 1
        # subroutineDec
        while (i < len(contents) and ( contents[i].is_keyword() and ( contents[i].content_is(["constructor", "function", "method"]) ) ) ):
            class_code, i = self._compileSubroutine(contents, class_code, i)
        class_code += [contents[i]]
        return class_code, i


    def _compileSubroutine(self, contents, class_code, i):
        '''
        Compiles a subroutine.
        '''
        self._reset_symbols(False)
        class_code += ["<subroutineDec>"]
        # ('constructor'|'function'|'method') ('void'|type) subroutineName
        method_type = contents[i].content
        self.new_compiled.append(f"function {self.cur_class}.{contents[i+2].content} ")
        if method_type == "method":
            self.new_compiled.append(f"push argument 0")
            self.new_compiled.append(f"pop pointer 0")
            self.method_symbols["this"] = { "num": 0, "kind": "argument", "type": self.cur_class }
            self.method_symbols["arg"] += 1
        class_code += contents[i:i+3]
        i += 3
        # (
        class_code += [contents[i]]
        i += 1
        # parameterList
        class_code += ["<parameterList>"]
        # parameters
        num_vars = 0
        while contents[i].content != ")":
            if contents[i+1].content in [",", ")"]:
                var_type = contents[i-1].content
                self.method_table[f"{contents[i].content}"] = { "num": self.method_symbols["arg"], "kind": "argument", "type": var_type }
                self.method_symbols["arg"] += 1

            class_code += [contents[i]]
            i += 1
        class_code += ["</parameterList>"]
        class_code += [contents[i]] # )
        i += 1
        # subroutineBody
        class_code += ["<subroutineBody>"]
        class_code += [contents[i]] # {
        i += 1
        num_vars = 0
        while not (contents[i].tag == "symbol" and contents[i].content == "}"):
            # varDec
            while (contents[i].tag == "keyword" and contents[i].content == "var"):
                class_code += ["<varDec>"]
                num_vars += 1
                self.method_table[f"{contents[i+2].content}"] = { "num": self.method_symbols["local"], "kind": "local", "type": contents[i+1].content }
                self.method_symbols["local"] += 1
                while not ( contents[i].tag == "symbol" and contents[i].content == ";" ):
                    if contents[i].content == ",":
                        self.method_table[f"{contents[i+1].content}"] = { "num": self.method_symbols["local"], "kind": "local" }
                        self.method_symbols["local"] += 1
                        num_vars += 1
                    class_code += [contents[i]]
                    i += 1
                class_code += [contents[i]] # ;
                i += 1
                class_code += ["</varDec>"]
            if method_type != "method": 
                self.new_compiled[-1] += str(num_vars) 
            else: 
                self.new_compiled[-3] += str(num_vars) 
            # statements

            if method_type == "constructor":
                let_index = i
                let_count = 0
                while contents[let_index].content != "return":
                    if contents[let_index].content == "let":
                        let_count += 1
                    let_index += 1
                self.new_compiled.append(f"push constant {len(self.class_table)}") 
                self.new_compiled.append(f"call Memory.alloc 1")
                self.new_compiled.append(f"pop pointer 0")
            if contents[i].tag == "keyword" and contents[i].content_is(["let", "if", "while", "do", "return"]):
                class_code += ["<statements>"]
                while contents[i].tag == "keyword" and contents[i].content_is(["let", "if", "while", "do", "return"]):
                    class_code, i = self._compile_statements(contents, class_code, i)
                class_code += ["</statements>"]

        class_code += [contents[i]]
        i += 1

            

        class_code += ["</subroutineBody>"]
        class_code += ["</subroutineDec>"]

        return class_code, i


    def _compile_statements(self, contents, class_code, i):
        '''
        Compiles statements.
        '''
        while contents[i].tag == "keyword" and contents[i].content_is(["let", "if", "while", "do", "return"]):
            if contents[i].content == "let":
                class_code += ["<letStatement>"]
                class_code += contents[i:i+2] # let varName
                local_dec = f"pop {self._get_table_values(contents, i+1)}"
                i += 2
                is_arr = False
                if contents[i].content == "[":
                    
                    is_arr = True
                    class_code += [contents[i]] # [
                    i += 1
                    a_i = i
                    class_code, i = self._compile_expressions(contents, class_code, i)
                    self.new_compiled.append(f"push {self._get_table_values(contents, a_i-2)}")
                    
                    self.new_compiled.append("add")

                    
                    class_code += [contents[i]] # ]
                    i += 1
                class_code += [contents[i]] # = 
                i += 1

                class_code, i = self._compile_expressions(contents, class_code, i, True)
                if is_arr:
                    self.new_compiled.append("pop temp 0")
                    self.new_compiled.append("pop pointer 1")
                    self.new_compiled.append("push temp 0")
                    self.new_compiled.append("pop that 0")
                if contents[i].content == ")" and contents[i+1].content == ";":
                    class_code += contents[i:i+2] 
                    i += 2
                if contents[i].content == ";":
                    class_code += [contents[i]] # ;
                    i += 1
                if not is_arr:
                    self.new_compiled.append(local_dec)
                class_code += ["</letStatement>"]
            elif contents[i].content == "if":
                class_code += ["<ifStatement>"]
                class_code += contents[i:i+2] # if (
                i += 2
                class_code, i = self._compile_expressions(contents, class_code, i)
                self.new_compiled.append("not")

                if_label = self.create_label()
                end_if = self.create_label()
                self.new_compiled.append(f"if-goto {end_if}")

                class_code += contents[i:i+2] # ) {
                i += 2
                class_code += ["<statements>"]
                while not ( contents[i].tag == "symbol" and contents[i].content == "}" ):
                    class_code, i = self._compile_statements(contents, class_code, i)
                class_code += ["</statements>"]
                class_code += [contents[i]] # }
                i += 1
                self.new_compiled.append(f"goto {if_label}")
                self.new_compiled.append(f"label {end_if}")
                if contents[i].content == "else" and contents[i].tag == "keyword":
                    class_code += contents[i:i+2] # else {
                    i += 2
                    class_code += ["<statements>"]
                    while not ( contents[i].tag == "symbol" and contents[i].content == "}" ):
                        class_code, i = self._compile_statements(contents, class_code, i)
                        
                    class_code += ["</statements>"]
                    
                    class_code += [contents[i]] # }
                    i += 1
                self.new_compiled.append(f"label {if_label}")
                class_code += ["</ifStatement>"]
            elif contents[i].content == "do":
                class_code += ["<doStatement>"]
                class_code, i = self._do_expression(contents, class_code, i)
                class_code += ["</doStatement>"]
            elif contents[i].content == "return":
                class_code += ["<returnStatement>"]
                class_code += [contents[i]] # return
                i += 1


                if contents[i].content == ";":
                    self.new_compiled.append("push constant 0")
                    self.new_compiled.append('return')
                    class_code += [contents[i]] # ;
                    i += 1
                else:
                    is_this = False
                    if contents[i].content == "this":
                        self.new_compiled.append(f"push pointer 0")
                        self.new_compiled.append(f"return")
                        is_this = True
                    class_code, i = self._compile_expressions(contents, class_code, i)
                    if not is_this:
                        self.new_compiled.append('return')
                    class_code += [contents[i]] # ;
                    i += 1
                class_code += ["</returnStatement>"]
            elif contents[i].content == "while":
                while_label = self.create_label()
                self.new_compiled.append(f"label {while_label}")
                class_code += ["<whileStatement>"]
                class_code += contents[i:i+2] # while (
                i += 2
                class_code, i = self._compile_expressions(contents, class_code, i)
                self.new_compiled.append("not")
                goto_label = self.create_label()
                self.new_compiled.append(f"if-goto {goto_label}")
                class_code += contents[i:i+2] # ) {
                i += 2
                class_code += ["<statements>"]
                while not ( contents[i].tag == "symbol" and contents[i].content == "}" ):
                    class_code, i = self._compile_statements(contents, class_code, i)
                class_code += ["</statements>"]
                class_code += [contents[i]] # }
                i += 1
                class_code += ["</whileStatement>"]
                self.new_compiled.append(f"goto {while_label}")
                self.new_compiled.append(f"label {goto_label}")
            else:
                break
        return class_code, i

    def table(self, key=None):

        if key in self.method_table.keys():
            return self.method_table[key]
        elif key in self.class_table.keys():
            return self.class_table[key]
        elif key is None:
            return list(self.class_table.keys()) + list(self.method_table.keys())
        raise KeyError(f"{key} not in tables")


    def _do_expression(self, contents, class_code, i, is_do=True):
        '''
        Compiles a do expression.
        '''
        num_vars = 0
        not_object = True
        if contents[i+1].content in self.table():
            self.new_compiled.append(f"push {self._get_table_values(contents, i+1)}")
            do_compiled_arr = [self.table(contents[i+1].content)["type"]]
            not_object = False
            num_vars += 1
        elif contents[i].content == ".":
            do_compiled_arr = [contents[i-1].content]
        else: 
            do_compiled_arr = []
        while not ( contents[i].content == "(" and contents[i].tag == "symbol" ):
            if contents[i].content == ".":
                not_object = True
            if ( contents[i].content != "do" and not_object ):
                do_compiled_arr.append(contents[i].content)
            class_code += [contents[i]]
            i += 1
        class_code += [contents[i]] # (
        i += 1
        class_code += ["<expressionList>"]
        # TODO: num_vars may be counting wrong.
        
        if ( len(do_compiled_arr) > 0 and do_compiled_arr[0] in self.method_names ):
            self.new_compiled.append("push pointer 0")
        has_this = True
        while not ( contents[i].content == ")" and contents[i].tag == "symbol" ):
            if has_this and (contents[i].content == "this"):
                self.new_compiled.append("push pointer 0")
            num_vars += 1
            class_code, i = self._compile_expressions(contents, class_code, i)
            if contents[i].content == "," and contents[i].tag == "symbol":
                class_code += [contents[i]] # ,
                i += 1
        class_code += ["</expressionList>"]
        class_code += [contents[i]] # )
        i += 1
        if is_do:
            class_code += [contents[i]] # ;
            i += 1
        if do_compiled_arr[0] in self.method_names:
            num_vars += 1
            cur_method_name = do_compiled_arr[0]
            do_compiled_arr[0] = f"{self.cur_class}." + cur_method_name
        elif do_compiled_arr[0][0].islower():
            do_compiled_arr[0] = do_compiled_arr[0].capitalize()
            num_vars += 1
        self.new_compiled.append(f"call {''.join(do_compiled_arr)} {num_vars}")
        if is_do:
            self.new_compiled.append("pop temp 0")
        return class_code, i
    

    def _get_table_values(self, contents, i):
        key = contents[i].content
        if key in self.method_table.keys(): 
            return f"{self.method_table[key]['kind']} {self.method_table[key]['num']}"
        elif key in self.class_table.keys(): 
            return f"{self.class_table[key]['kind']} {self.class_table[key]['num']}"
        else:
            raise KeyError(f"{key} not in any table.")


    def _compile_expressions(self, contents, class_code, i, is_let=False):
        '''
        Compiles an expression.
        '''
        if re.match(self.token_pattern, contents[i].content):
            class_code += ["<expression>"]
            while True:
                class_code, i, is_do = self._compile_term(contents, class_code, i)
                if ( contents[i].content == ")" ) and is_let:
                    class_code += [contents[i]] 
                    i += 1
                    class_code += ["</term>"]
                    class_code += ["</expression>"]
                    break
                if not ( ( contents[i].content == ")" ) and contents[i+1].content != "{" and contents[i+1].content != ";" and contents[i+1].content != ","):
                    class_code += ["</term>"]
                    class_code += ["</expression>"]
                    if not is_do:
                        class_code += [contents[i]] # ;
                        i += 1
                    break
                if ( contents[i].content == ")" ):
                    class_code += ["</term>"]
                    class_code += ["</expression>"]
                    class_code += [contents[i]] 
                    i += 1
                    break
        return class_code, i
    

    def _compile_term(self, contents, class_code, i):
        '''
        Compiles a term.
        '''
        class_code += ["<term>"]
        is_do = True
        if ( contents[i].content == "(" ):
            class_code += [contents[i]]
            i += 1
            class_code, i = self._compile_expressions(contents, class_code, i)
        elif not re.match(self.opterms, contents[i].content):
            #if type(contents[i]) == BaseXML and contents[i].tag == "integerConstant":
            #    self.new_compiled.append(f"push constant {contents[i].content}")
            tag_type = None
            if type(contents[i]) == BaseXML and contents[i].tag == "integerConstant":
                tag_type = "integerConstant"
            elif type(contents[i]) == BaseXML and contents[i].content in self.method_table.keys():
                tag_type = "method"
            elif type(contents[i]) == BaseXML and contents[i].content in self.class_table.keys():
                tag_type = "class"
            elif type(contents[i]) == BaseXML and contents[i].content == "true":
                tag_type = "true"
            elif type(contents[i]) == BaseXML and contents[i].content == "false":
                tag_type = "false"

            if contents[i].tag == "stringConstant":
                str_len = len(contents[i].content)
                self.new_compiled.append(f"push constant {str_len}")
                self.new_compiled.append(f"call String.new 1")
                for c in list(contents[i].content):
                    self.new_compiled.append(f'push constant {self.char_dict[c]}')
                    self.new_compiled.append('call String.appendChar 2')
            
            if contents[i].content == "null":
                self.new_compiled.append("push constant 0")
            



            if tag_type == "integerConstant":
                self.new_compiled.append(f"push constant {contents[i].content}")
            elif ( tag_type == "method" or tag_type == "class" ) and contents[i+1].content != "[":
                self.new_compiled.append(f"push {self._get_table_values(contents, i)}")
            elif tag_type == "true":
                self.new_compiled.append("push constant 1")
                self.new_compiled.append("neg")
            elif tag_type == "false":
                self.new_compiled.append("push constant 0")


            class_code += [contents[i]] 
            i += 1
            if contents[i].content == "[":
                a_i = i-1
                class_code += [contents[i]] 
                i += 1
                class_code, i = self._compile_expressions(contents, class_code, i)
                self.new_compiled.append(f"push {self._get_table_values(contents, a_i)}")
                self.new_compiled.append("add")
                self.new_compiled.append("pop pointer 1")
                self.new_compiled.append("push that 0")
                class_code += [contents[i]] 
                i += 1
            if contents[i].content == "." and contents[i].tag == "symbol":
                class_code, i = self._do_expression(contents, class_code, i, False)
                is_do = False
        if re.match(self.opterms, contents[i].content):
            if not re.match(self.unary, contents[i].content) or self._is_subtraction(contents, class_code, i) and contents[i].content != "~":
                class_code += ["</term>"]  
                op = contents[i].content
                tag_type = None
                if type(op) == BaseXML and op.tag == "integerConstant":
                    tag_type = "integerConstant"



                class_code += [contents[i]]
                i += 1
                class_code, i, is_do = self._compile_term(contents, class_code, i)
                if op == "-":
                    self.new_compiled.append(f"sub")
                elif op == "+":
                    self.new_compiled.append(f"add")
                elif op == "*":
                    self.new_compiled.append(f"call Math.multiply 2")
                elif op == "&gt;":
                    self.new_compiled.append(f"gt")
                elif op == "&lt;":
                    self.new_compiled.append("lt")
                elif op == "&amp;":
                    self.new_compiled.append(f"and")
                elif op == "|":
                    self.new_compiled.append("or")
                elif op == "=":
                    self.new_compiled.append(f"eq")
                elif tag_type == "integerConstant":
                    self.new_compiled.append(f"push constant {contents[i].content}")
                elif op == "/":
                    self.new_compiled.append(f"call Math.divide 2")

            else:
                op = contents[i].content
                class_code += [contents[i]]
                i += 1
                class_code, i, is_do = self._compile_term(contents, class_code, i)
                if op == "-":
                    self.new_compiled.append("neg")
                else:
                    self.new_compiled.append("not")
                class_code += ["</term>"] 
        return class_code, i, is_do
    
    def _is_subtraction(self, contents, class_code, i):
        if contents[i].content != "-" or type(class_code[-1]) == str:
            return False
        if class_code[-1].tag == "identifier" or class_code[-1].tag == "integerConstant" or class_code[-1].tag == "stringConstant" or class_code[-1].content == ")":
            return True
        return False


    def parse_xml(self, contents):
        '''
        Parses xml into BaseXML.
        '''
        parsed_xml = []
        for line in contents:
            parsed_xml.append(BaseXML(line))
        return parsed_xml


class BaseXML:


    def __init__(self, line):
        '''
        Initializes a BaseXML instance used to work with individual lines of xml.
        '''
        self.tag_pattern = r"<\s*([^/\s>]+)[^>]*>"
        self.content_pattern = r"> (.*?) <"
        self.tag = self._get_tag(line)
        self.content = self._get_content(line)


    def is_keyword(self):
        if self.tag == "keyword":
            return True
        return False
    

    def content_is(self, contents):
        for content in contents:
            if self.content == content:
                return True
        return False


    def _get_tag(self, line):
        tag = re.findall(self.tag_pattern, line)
        if len(tag) < 1:
            return ""
        return tag[0]
    

    def _get_content(self, line):
        content = re.findall(self.content_pattern, line)
        if len(content) < 1:
            return ""
        return content[0] 


    @classmethod
    def many_to_str(cls, contents):
        '''
        Converts a list of BaseXML and strings to a list of strings.
        '''
        new_contents = []
        for line in contents:
            if type(line) != BaseXML:
                new_contents.append(line)
            else:
                new_contents.append(line.to_str())
        return new_contents                
    

    def to_str(self):
        return f"<{self.tag}> {self.content} </{self.tag}>"