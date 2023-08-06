from lib2to3.pgen2 import token
import os 
from enum import Enum
from pprint import pprint 

class TokenType(Enum):
    COMMAND = 0
    COMPONENT_TYPE = 1
    ARGUMENT = 2
    TAG = 3
    VALUE = 4

class Token():
    def __init__(self, token_type, token_value):
        self.token_type = token_type
        self.token_value = token_value
    def __str__(self):
            return self.token_value

class TokenParser():

    def parse_line(line):

        # Clean line
        line = line.strip()

        # Verify comment
        assert line[0] == '#'

        # Strip comment
        line = line[1:].strip()

        # Tokenize
        tokens = line.split(" ")

        # Remove empty tokens
        tokens = [token for token in tokens if token.strip() is not '']

        # Check to make sure its non-empty
        if tokens == None or len(tokens) == 0:
            return []

        # Skip if token valid
        valid_tokens = ['@doc', '@input', '@flag','@output']
        if tokens[0].strip() not in valid_tokens:
            return []

        # Validate token count
        two_token_types = ['@input', '@output']
        if tokens[0].strip() in two_token_types and len(tokens) < 2:
            return []

        # Ensure inputs and outputs specifiy type
        if tokens[0].strip() != '@doc':
            tokens = [TokenParser.parse_token(token) for token in tokens]
        else:

            # Get markdown content
            doc_content = line[line.find('@doc') + len('@doc'):].strip()
            component_type = 'markdown'
            
            # Process doc token
            tokens = [TokenParser.parse_token('@doc'), Token(TokenType.COMPONENT_TYPE, component_type), Token(TokenType.VALUE, doc_content.strip())]

        tokens = [token for token in tokens if token is not None]
        return tokens

    def parse_token(token):
        token = token.strip()
        valid_component_types = ['number', 'heading', 'table', 'graph', 'scatter-graph', 'line-graph', 'image', 'doc']
        if token.startswith("#"):
            return Token(TokenType.TAG, token)
        elif token.startswith("@"):
            return Token(TokenType.COMMAND, token)
        elif token.startswith("--") and len(token) > 2:
            return Token(TokenType.ARGUMENT, token[2:])
        elif token in valid_component_types:
            return Token(TokenType.COMPONENT_TYPE, token)
        else:
            return None

class TokenChain():
   
    def __init__(self, line):
        line = line.strip()
        self.is_token_chain = False
        self.tokens = []
        if len(line) == 0 or line[0] != '#':
            return
        self.tokens = TokenParser.parse_line(line)

    def get_tokens_str(self):
        if not self.is_valid():
            return "[Invalid token chain]"

        out = '['
        for token in self.tokens[:-1]:
            out += str(token) + ', '
        if len(self.tokens) > 0:
            out += str(self.tokens[-1])
        out += ']'
        return out

    def __str__(self):
        out = 'Token' + '\n\tCommand: ' + self.get_command() + '\n'
        out += '\tComponent Type: ' + self.get_component_type() + '\n'
        out += "\tTokens: " + self.get_tokens_str() + "\n"
        out +=  '\tTags: ' + "\n"
        for tag in self.get_tags():
            out += "\t" + tag + "\n"
        out += '\tArgs' + "\n"
        for arg in self.get_args():
            out += "\t" + arg + "\n"
        return out


    def is_valid(self):

        # Verify tokens exist
        if len(self.tokens) == 0:
            return False

        # Verify command exists
        if self.tokens[0].token_type != TokenType.COMMAND:
            return False

        # We dont need to verify compnent type if we're just enabling or disabling
        if self.tokens[0].token_value == '@flag' or self.tokens[0].token_value == '@doc':
            return True

        # Verify component type exists
        if self.tokens[1].token_type != TokenType.COMPONENT_TYPE:
            return False
        return True

    
    def get_tags(self):
        tags = []
        for token in self.tokens:
            if token.token_type == TokenType.TAG:
                tags.append(token.token_value)
        return tags

    def get_args(self):
        args = []
        for token in self.tokens:
            if token.token_type == TokenType.ARGUMENT:
                args.append(token.token_value)
        return args

    def get_command(self):
        if self.tokens[0].token_type == TokenType.COMMAND:
            return self.tokens[0].token_value
        return None

    def get_component_type(self):
        if self.tokens[1].token_type == TokenType.COMPONENT_TYPE:
            return self.tokens[1].token_value

    def get_component_value(self):
        if self.tokens[2].token_type == TokenType.VALUE:
            return self.tokens[2].token_value
        return None

class TagMap():
    def __init__(self):
        self.tags = {}

    def enable_tag(self, tag, prop):
        tag = tag.strip()
        if tag not in self.tags:
            self.tags[tag] = {}
        self.tags[tag][prop] = True

    def disable_tag(self, tag, prop):
        tag = tag.strip()
        if tag not in self.tags:
            self.tags[tag] = {}
        self.tags[tag][prop] = False

    def is_tag_enabled(self, tag, prop):
        tag = tag.strip()
        if tag not in self.tags:
            return True
        if prop not in self.tags[tag]:
            return True
        return self.tags[tag]

    def get_prop_value(self, tag_list, prop):
        val = None
        for tag in tag_list:
            tag = tag.strip()
            if tag in self.tags and prop in self.tags[tag]:
                val = self.tags[tag][prop]
        return val

class Line():
    def __init__(self, line):
        self.line = line
        strip_line = self.line.strip()

        # Iniitialize variables
        self.comment = False 
        self.lhs = ''
        self.rhs = ''

        # Check if line is a comment
        if len(strip_line) == 0:
            return
        self.comment = strip_line[0] == '#'

        # Parse sides of line
        if '=' not in strip_line:
            self.lhs = strip_line
            self.rhs = ''
        else: 
            try:
                self.lhs = line.split('=')[0].strip()
                self.rhs = line.split('=')[1].strip()
            except Exception as e:
                print('Failed to parse line: ' + line)
                print('Exception: ' + str(e))
                raise e
              
    def is_comment(self):
        return self.comment

    def get_lhs(self):
        return self.lhs

    def get_rhs(self):
        return self.rhs

    def get_line(self):
        return self.line

class LineParser():
    def parse_line(line):
        return Line(line)

class LineTransformer():
    def transform_script(lines):
        
        # Tag map
        tag_map = TagMap()

        # Skip next line n lines 
        skip_counter = 0

        # Main pass
        pass_1 = []

        # Transform lines
        for i, line in enumerate(lines):

            # Skip lines
            if skip_counter > 0:
                skip_counter -= 1
                continue

            # Tokenize Line
            token_chain = TokenChain(line)

            # Parse line
            curr_line = LineParser.parse_line(line)
            next_line = None
            if i < len(lines) - 1:
                next_line = LineParser.parse_line(lines[i + 1])

            # Process commands                    
            if token_chain.is_valid():
                
                # Handle flags
                if token_chain.get_command() == '@flag':
                    valid_flags = ['enable', 'disable', 'nostop']
                    if len(token_chain.get_args()) > 0 and token_chain.get_args()[0] in valid_flags:
                        for tag in token_chain.get_tags():
                            if token_chain.get_args()[0] == 'enable':
                                tag_map.disable_tag(tag, 'disable')
                            else:
                                tag_map.enable_tag(tag, token_chain.get_args()[0])
                    pass_1.append(line)
                    continue

                # Handle no stop flags
                if token_chain.get_command() == '@nostop':
                    for tag in token_chain.get_tags():
                        tag_map.enable_tag(tag, 'nostop')
                    pass_1.append(line)
                    continue

                # Handle disabled status
                if 'disable' in token_chain.get_args():
                    pass_1.append(line)
                    continue
                elif tag_map.get_prop_value(token_chain.get_tags(), 'disable') == True:
                    pass_1.append(line)
                    continue

                if '@input' == token_chain.get_command() and next_line != None:

                    # ensure next line is not a comment
                    if next_line.is_comment():
                        pass_1.append(line)
                        continue
                            
                    # get name of variable
                    lhs = next_line.get_lhs()

                    # get cast type 
                    input_component_type = token_chain.get_component_type()
                    if input_component_type == 'number':
                        input_type = "float"

                    # append fodder
                    pass_1.append(line)
                    pass_1.append(f"app.createInput({i}, 'Variable {lhs}', '')")
                    pass_1.append(f'state = {input_type}(app.waitForInput())')
                    pass_1.append('app.hideInput()')
                    pass_1.append(next_line.get_lhs() + ' = state')
                    skip_counter = 1
                    continue

                if '@output' == token_chain.get_command() and next_line != None:

                    # ensure next line is not a comment
                    if next_line.is_comment():
                        pass_1.append(line)
                        continue
                            
                    # get name of variable
                    lhs = next_line.get_lhs()

                    # get type of component
                    componentType = token_chain.get_component_type()
                
                    # append fodder
                    pass_1.append(line)
                    pass_1.append(next_line.get_line())
                    pass_1.append(f"app.createOutput({i}, '{lhs}', {lhs}, '{componentType}', '')")

                    # add stop
                    if tag_map.get_prop_value(token_chain.get_tags(), 'nostop') != True and 'nostop' not in token_chain.get_args():
                        pass_1.append(f"app.waitForNext()")
                    skip_counter = 1
                    continue

                if '@doc' == token_chain.get_command():
                    pass_1.append(line)
                    markdown_text = token_chain.get_component_value().replace("'", "\\'")
                    pass_1.append(f"app.createOutput({i - 1}, '', '{markdown_text}', '{token_chain.get_component_type()}', '')")
                    continue


            # Add normal line
            pass_1.append(line)

        # Return transformed lines
        return pass_1


def process_script(runner_path, launch_command, code_path, dev=False, launch=True):
    
    # Read contents of decorated.py
    original_contents = open(code_path).read()
    original_contents_lines = original_contents.split('\n')

    # Prepend import
    if dev:
        original_contents_lines.insert(0, f'app = artemis("{runner_path}", "{launch_command}", "{code_path}", {launch}, {dev})')
        original_contents_lines.insert(0, 'from artemis_labs import artemis')
        original_contents_lines.insert(0, 'sys.path.append(\'./artemis_labs/src/\')')
        original_contents_lines.insert(0, 'import sys')
    else:
        original_contents_lines.insert(0, f'app = artemis("{runner_path}", "{launch_command}", "{code_path}", {launch}, {dev})')
        original_contents_lines.insert(0, 'from artemis_labs import artemis')

    
    # Transform lines
    transformed_contents_lines = LineTransformer.transform_script(original_contents_lines)

    # Dump back to file
    new_path = code_path.strip()[:-3] + '_artemis.py'
    out_path = new_path
    print(f'saving to {out_path}')
    with open(out_path, 'w') as f:
        for line in transformed_contents_lines:
            f.write(line + '\n')
    return new_path