import re
from sqlite3 import SQLITE_CREATE_INDEX

class Analyzer():

    def __init__(self):
        self.analyzed_code = ''

        # Read the tokens
        with open('tokens\delimiters.txt', 'r') as f:
            self.DELIMITERS = f.read().split('\n')
        
        with open('tokens\keywords.txt', 'r') as f:
            self.KEYWORDS = f.read().split('\n')
        
        with open('tokens\operators.txt', 'r') as f:
            self.OPERATORS = f.read().split('\n')

        self.COMMENTS = ['//', '/*']

    # TODO REGEX for floats
    def return_token_type(self, token):
        # Checks for delimiters, keywords and operators
        if token in self.COMMENTS:
            return 'comment'
        elif token in self.DELIMITERS:
            return 'delimiter'
        elif token in self.KEYWORDS:
            return 'keyword'
        elif token in self.OPERATORS:
            return 'operator'
        elif token.isdigit():
            return 'int'
        elif re.match('[_a-zA-Z][_a-zA-Z0-9]{0,30}', token):
            return 'identifier'
        return ''

    def tokenize_line(self, line):
        tokens = []

        last = 0
        current = 0

        while current < len(line):
            if line[current] in self.DELIMITERS or line[current] == ' ':

                if line[last:current] != '':
                    tokens.append(line[last:current])

                if line[current] != ' ':
                    tokens.append(line[current])
                last = current + 1
            current += 1

        return tokens


    def analyze_code(self, code):
        # Initiate output
        output = ''

        # Split the code in lines (removing blanks)
        code = [x.strip() for x in code.split('\n') if x.strip() != '']

        # Iterate through each line and tokenize them
        tokens = []
        for line in code:
            tokens.append(self.tokenize_line(line))


        # Iterate again to validate and transform the tokens
        # into end user form
        for line_idx, line_tokens in enumerate(tokens):
            token_idx = 0
            while token_idx < len(line_tokens):
                
                # If we are in a string
                if line_tokens[token_idx] == '"':
                    output += f'{line_tokens[token_idx]} - delimeter, {len(line_tokens[token_idx])}, linia {line_idx}\n'

                    # We gather all of the string elements
                    string_idx = token_idx + 1
                    string_output = ''
                    while line_tokens[string_idx] != '"':
                        string_output += f' {line_tokens[string_idx]}'
                        string_idx += 1
                    
                    # Add the string and the closing "
                    output += f'{string_output[1:]} - string, {len(string_output[1:])}, linia {line_idx}\n'
                    output += f'{line_tokens[string_idx]} - delimeter, {len(line_tokens[string_idx])}, linia {line_idx}\n'

                    # Increment the token_idx
                    token_idx = string_idx + 1

                token_type = self.return_token_type(line_tokens[token_idx])
                if token_type != '':
                    output += f'{line_tokens[token_idx]} - {token_type}, {len(line_tokens[token_idx])}, linia {line_idx}\n'
                else:
                    output += f'{line_tokens[token_idx]} - unknown, {len(line_tokens[token_idx])}, linia {line_idx}\n'

                token_idx += 1

        return output


    def analyzed_code_to_json(self):
        return "Translated Json"