import re

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
        self.IDENTIFIER_RE = '[_a-zA-Z][_a-zA-Z0-9]{0,30}'
        self.FLOAT_RE = '([0-9]*[.])?[0-9]+'

    # TODO REGEX for floats when multiple dots are in the number
    def return_token_type(self, token):
        # Returns token type
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
        elif re.match(self.FLOAT_RE, token):
            return 'float'
        elif re.match(self.IDENTIFIER_RE, token):
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
        # Initialize output
        output = ''

        # Initialize errors
        errors = ''

        # Split the code in lines (removing blanks)
        code = [x.strip() for x in code.split('\n') if x.strip() != '']

        # Iterate through each line and tokenize them
        tokens = []
        for line in code:
            tokens.append(self.tokenize_line(line))


        # Iterate again to validate and transform the tokens
        # into end user form
        for line_idx, line_tokens in enumerate(tokens):

            try:
                token_idx = 0
                while token_idx < len(line_tokens):

                    # If we are in a STRING
                    if line_tokens[token_idx] == '"':

                        # We gather all of the string elements
                        string_idx = token_idx + 1
                        string_output = ''

                        # While the closing delimiter is not found or we got to the end
                        while line_tokens[string_idx] != '"':
                            string_output += f' {line_tokens[string_idx]}'
                            string_idx += 1

                            # If we reached end of line
                            if not string_idx < len(line_tokens):
                                break

                        # Closing delimiter is found
                        if string_idx < len(line_tokens):
                            if line_tokens[string_idx] == '"':
                                # Add the the delimiters and string to the output
                                output += f'{line_tokens[string_idx]} - delimeter, {len(line_tokens[string_idx])}, linia {line_idx + 1}\n'
                                output += f'{string_output[1:]} - string, {len(string_output[1:])}, linia {line_idx + 1}\n'
                                output += f'{line_tokens[string_idx]} - delimeter, {len(line_tokens[string_idx])}, linia {line_idx + 1}\n'

                                # Increment the token_idx
                                token_idx = string_idx + 1

                    # If we are in a CHAR
                    if line_tokens[token_idx] == "'":

                        # We gather all of the string elements
                        string_idx = token_idx + 1
                        string_output = ''

                        # While the closing delimiter is not found or we got to the end
                        while line_tokens[string_idx] != "'":
                            string_output += f' {line_tokens[string_idx]}'
                            string_idx += 1

                            if not string_idx < len(line_tokens):
                                break

                        if string_idx < len(line_tokens):
                            if line_tokens[string_idx] == "'":
                                # Add the the delimiters and char to the output
                                output += f'{line_tokens[string_idx]} - delimeter, {len(line_tokens[string_idx])}, linia {line_idx + 1}\n'
                                output += f'{string_output[1:]} - char, {len(string_output[1:])}, linia {line_idx + 1}\n'
                                output += f'{line_tokens[string_idx]} - delimeter, {len(line_tokens[string_idx])}, linia {line_idx + 1}\n'

                                # Increment the token_idx
                                token_idx = string_idx + 1

                    # Some cases where the token_idx might be out of range
                    if token_idx < len(line_tokens):

                        token_type = self.return_token_type(line_tokens[token_idx])
                        if token_type != '':
                            output += f'{line_tokens[token_idx]} - {token_type}, {len(line_tokens[token_idx])}, linia {line_idx + 1}\n'
                        else:
                            errors += f'Eroare linia {line_idx + 1}: {line_tokens[token_idx]}\n'

                        token_idx += 1

            # TODO: Log in a file
            except BaseException as err:
                # Logs
                print(f'Error:\n{repr(err)}\nOutput:\n{output}\nCode:\n{code}\nTokens:\n{line_tokens}\n')

        return output, errors


    def analyzed_code_to_json(self):
        return "Translated Json"