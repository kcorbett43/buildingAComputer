import sys
from pathlib import Path
import os
import writeToFile
import re

class JackTokenizer:


    def __init__(self):
        '''
        Initialize Jack Tokenizer with regular expressions for parsing.
        '''
        self._token_re()


    def tokenize(self, contents):
        '''
        Basic tokenizer for a Jack program.
        '''
        tokens = ["<tokens>"]
        contents = self.parse(contents)
        for token in contents:
            if re.match(self.keyword_pattern, token):
                tokens += [f"<keyword> {token} </keyword>"]
            elif re.match(self.symbol_pattern, token):
                if token == ">":
                    token = "&gt;"
                elif token == "<":
                    token = "&lt;"
                elif token == "&":
                    token = "&amp;"
                elif token == "\"":
                    token = "&quot;"
                tokens += [f"<symbol> {token} </symbol>"]
            elif re.match(self.integer_constant_pattern, token):
                tokens += [f"<integerConstant> {token} </integerConstant>"]
            elif re.match(self.string_constant_pattern, token):
                token = token.replace("\"", '')
                tokens += [f"<stringConstant> {token} </stringConstant>"]
            elif re.match(self.identifier_pattern, token):
                tokens += [f"<identifier> {token} </identifier>"]        
        tokens += ["</tokens>"]
        return tokens


    def parse(self, contents):
        '''
        Gets all relevant tokens from the Jack program.
        '''
        parsed_contents = []
        for line in contents:
            parsed_contents += re.findall(self.token_pattern, line)
        return parsed_contents
    

    def _token_re(self):
        '''
        Initializes regular expressions for finding tokens.
        '''
        self.keyword_pattern = r'\b(?:class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)\b'
        self.symbol_pattern = r'[\{\}\(\)\[\]\.\,\;\+\-\*\/&\|<>=~]'
        self.integer_constant_pattern = r'\b(?:0|[1-9][0-9]{0,4})\b'
        self.string_constant_pattern = r'"[^"\n]*"'
        self.identifier_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        self.token_pattern = f'{self.keyword_pattern}|{self.symbol_pattern}|{self.integer_constant_pattern}|{self.string_constant_pattern}|{self.identifier_pattern}'