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

    def return_token_type(self, token):
        # Checks for delimiters, keywords and operators
        if token in self.DELIMITERS:
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

        # Iterate through each line
        tokens = []
        for line in code:
            tokens.append(self.tokenize_line(line))


        output = ''
        for line_idx, line_tokens in enumerate(tokens):
            for token in line_tokens:
                token_type = self.return_token_type(token)

                if token_type != '':
                    output += f'{token} - {token_type}, {len(token)}, linia {line_idx}\n'
                else:
                    output += f'{token} - unknown, {len(token)}, linia {line_idx}\n'
        return output


    def analyzed_code_to_json(self):
        return "Translated Json"