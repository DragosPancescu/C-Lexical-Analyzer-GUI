import re
import traceback
import json

class Analyzer():

    def __init__(self):
        self.analyzed_code_json = []
        self.errors_json = []

        # Read the tokens
        with open('tokens\delimiters.txt', 'r') as f:
            self.DELIMITERS = f.read().split('\n')
        
        with open('tokens\keywords.txt', 'r') as f:
            self.KEYWORDS = f.read().split('\n')
        
        with open('tokens\operators.txt', 'r') as f:
            self.OPERATORS = f.read().split('\n')
        
        with open('tokens\directives.txt', 'r') as f:
            self.DIRECTIVES = f.read().split('\n')

        self.COMMENTS = ['//', '/*']
        self.IDENTIFIER_RE = '[_a-zA-Z][_a-zA-Z0-9]{0,30}'
        self.FLOAT_RE = '([0-9]*[.])?[0-9]+'

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
        elif token in self.DIRECTIVES:
            return 'directive'
        elif token.isdigit():
            return 'int'
        elif re.match(self.FLOAT_RE, token):
            return 'float'
        elif re.match(self.IDENTIFIER_RE, token):
            return 'identifier'
        elif token == '.':
            return 'access operator'
        return ''

    def tokenize_line(self, line):
        tokens = []

        last = 0
        current = 0

        while current < len(line):
            if line[current] in self.DELIMITERS or line[current] in [' '] or line[current] in self.OPERATORS:

                if line[last:current] != '':
                    tokens.append(line[last:current])

                if line[current] != ' ':
                    tokens.append(line[current])
                last = current + 1
            current += 1

        # Check if we have a remaining token left
        if line[last:current] != '':
            tokens.append(line[last:current])

        return tokens  


    def add_to_output_json(self, token, token_type, line):
        self.analyzed_code_json.append({token: [{'tip': token_type}, {'lungime': len(token)}, {"linia": line}]})


    def add_to_errors_json(self, token, line):
        self.errors_json.append({token: {'linia': line}})


    def serialize_output_and_errors(self):
        output = {'Analyzed Code': self.analyzed_code_json}
        errors = {'Errors': self.errors_json}

        output = json.dumps(output, indent=4)
        errors = json.dumps(errors, indent=4)

        return f'{output}\n{errors}'

    def reset_jsons(self):
        self.analyzed_code_json = []
        self.errors_json = []


    def extract_floats(self, float_token, line_idx):
        split_float_token = float_token.split('.')
        output = ''
        error = ''

        # If the float is .x or x. it is valid it can not be only a dot because that is a access operator
        if len(split_float_token) == 2:
            output += f'{float_token} - float, {len(float_token)}, linia {line_idx + 1}\n'
            self.add_to_output_json(float_token, 'float', line_idx + 1)
        else:
            while re.match(self.FLOAT_RE, float_token):
                match = re.match(self.FLOAT_RE, float_token)

                start = match.start()
                end = match.end()
                output += f'{float_token[start:end]} - float, {len(float_token[start:end])}, linia {line_idx + 1}\n'
                self.add_to_output_json(float_token[start:end], 'float', line_idx + 1)

                float_token = re.sub(self.FLOAT_RE, '', float_token, 1)
            
            if float_token != '':
                error += f'Eroare linia {line_idx + 1}: {float_token}\n'
                self.add_to_errors_json(float_token, line_idx + 1)

        return output, error

    def single_comment_handle(self, line_tokens, token_idx, line_idx):
        output = f'{line_tokens[token_idx]} - single line comment, {len(line_tokens[token_idx])}, linia {line_idx + 1}\n'
        self.add_to_output_json(line_tokens[token_idx], 'single line comment', line_idx + 1)
        token_idx += 1

        # Add the comment string and break the loop
        string_output = ''
        while token_idx < len(line_tokens):
            string_output += f' {line_tokens[token_idx]}'
            token_idx += 1

        output += f'{string_output[1:]} - comment string, {len(string_output[1:])}, linia {line_idx + 1}\n'
        self.add_to_output_json(string_output[1:], 'comment string', line_idx + 1)

        return output


    def directives_handle(self, line_tokens, token_idx, line_idx):
        output = f'{line_tokens[token_idx]} - directive, {len(line_tokens[token_idx])}, linia {line_idx + 1}\n'
        self.add_to_output_json(line_tokens[token_idx], 'directive', line_idx + 1)

        token_idx += 1

        # Add the directive string and break the loop
        string_output = ''
        while token_idx < len(line_tokens):
            string_output += f' {line_tokens[token_idx]}'
            token_idx += 1

        output += f'{string_output[1:]} - directive string, {len(string_output[1:])}, linia {line_idx + 1}\n'
        self.add_to_output_json(string_output[1:], 'directive string', line_idx + 1)

        return output

    
    def string_or_char_handle(self, line_tokens, token_idx, line_idx):

        # Add the delimiter
        output = f'{line_tokens[token_idx]} - delimeter, {len(line_tokens[token_idx])}, linia {line_idx + 1}\n'
        self.add_to_output_json(line_tokens[token_idx], 'delimeter', line_idx + 1)

        if token_idx == (len(line_tokens) - 1): 
            return output, token_idx

        # Stores either a " or a '
        delim = line_tokens[token_idx]

        # We gather all of the string elements
        string_idx = token_idx + 1
        string_output = ''

        # While the closing delimiter is not found or we got to the end
        while line_tokens[string_idx] != delim:
            string_output += f' {line_tokens[string_idx]}'
            string_idx += 1

            # If we reached end of line
            if not string_idx < len(line_tokens):
                break
        
        # Add the string
        output += f'{string_output[1:]} - string, {len(string_output[1:])}, linia {line_idx + 1}\n'
        self.add_to_output_json(string_output[1:], 'string', line_idx + 1)

        # Closing delimiter is found
        if string_idx < len(line_tokens):
            # Add the delimiter
            output += f'{line_tokens[string_idx]} - delimeter, {len(line_tokens[string_idx])}, linia {line_idx + 1}\n'
            self.add_to_output_json(line_tokens[string_idx], 'delimeter', line_idx + 1)
            
        return output, string_idx


    def reference_or_pointer_handle(self, line_tokens, token_idx, line_idx):
        already_added = False
        output = ''

        if line_tokens[token_idx][0] in ['&', '*'] and len(line_tokens[token_idx]) > 1:
            
            token_type = 'reference' if line_tokens[token_idx][0] == '&' else 'pointer'

            output += f'{line_tokens[token_idx][0]} - {token_type}, {len(line_tokens[token_idx][0])}, linia {line_idx + 1}\n'
            self.add_to_output_json(line_tokens[token_idx][0], token_type, line_idx + 1)

            output += f'{line_tokens[token_idx][1:]} - identifier, {len(line_tokens[token_idx][1:])}, linia {line_idx + 1}\n'
            self.add_to_output_json(line_tokens[token_idx][1:], 'identifier', line_idx + 1)

            already_added = True

        if line_tokens[token_idx] in ['&', '*'] and (token_idx == 0 or self.return_token_type(line_tokens[token_idx - 1]) != 'identifier'):
            
            token_type = 'reference' if line_tokens[token_idx] == '&' else 'pointer'

            output += f'{line_tokens[token_idx]} - {token_type}, {len(line_tokens[token_idx][0])}, linia {line_idx + 1}\n'
            self.add_to_output_json(line_tokens[token_idx], token_type, line_idx + 1)

            already_added = True

        # We can look back 2 tokens
        if token_idx - 1 >= 0 and token_idx - 2 >= 0:
            if line_tokens[token_idx] in ['&', '*'] and self.return_token_type(line_tokens[token_idx - 1]) == 'identifier' and self.return_token_type(line_tokens[token_idx - 2]) == 'keyword':
                
                token_type = 'reference' if line_tokens[token_idx] == '&' else 'pointer'

                output += f'{line_tokens[token_idx]} - {token_type}, {len(line_tokens[token_idx][0])}, linia {line_idx + 1}\n'
                self.add_to_output_json(line_tokens[token_idx], token_type, line_idx + 1)

                already_added = True

        return output, already_added


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

        # Iterate again to validate and transform the tokens into end user form
        for line_idx, line_tokens in enumerate(tokens):
            token_idx = 0

            try:
                while token_idx < len(line_tokens):
                    # Checks if we already added to the output
                    already_added = False
                    
                    # TODO: Multi line COMMENT

                    # If we are in a single line COMMENT
                    if line_tokens[token_idx] == '//':
                        
                        output += self.single_comment_handle(line_tokens, token_idx, line_idx)
                        break
                    
                    # If we encounter a directive
                    if self.return_token_type(line_tokens[token_idx]) == 'directive':

                        output += self.directives_handle(line_tokens, token_idx, line_idx)
                        break

                    # If & or * represents reference or pointer and not an operator
                    reference_or_pointer_output, already_added = self.reference_or_pointer_handle(line_tokens, token_idx, line_idx)
                    output += reference_or_pointer_output

                    # If we are in a STRING or CHAR
                    if line_tokens[token_idx] in ['"', "'"]:
                        
                        string_or_char_output, token_idx = self.string_or_char_handle(line_tokens, token_idx, line_idx)
                        output += string_or_char_output
                        already_added = True

                    if already_added == False:
                        token_type = self.return_token_type(line_tokens[token_idx])
                        if token_type != '':
                            
                            if token_type == 'float':
                                float_output, float_error = self.extract_floats(line_tokens[token_idx], line_idx)
                                output += float_output
                                errors += float_error
                            else:
                                output += f'{line_tokens[token_idx]} - {token_type}, {len(line_tokens[token_idx])}, linia {line_idx + 1}\n'
                                self.add_to_output_json(line_tokens[token_idx], token_type, line_idx + 1)
                        else:
                            errors += f'Eroare linia {line_idx + 1}: {line_tokens[token_idx]}\n'
                            self.add_to_errors_json(line_tokens[token_idx], line_idx + 1)
                
                    token_idx += 1

            # TODO: Log in a file
            except BaseException as err:
                # Logs
                traceback.print_exc()
                print(f'\nOutput:\n{output}\nCode:\n{code}\nTokens:\n{line_tokens}\n')

        self.analyzed_code = output
        return output, errors