from lark import Lark, Transformer, v_args
from pathlib import Path
import sys
from utils import same_values_unordered, flatten_str, check_type

# Define visitor
@v_args(inline=True)
class GCodeGenerator(Transformer):
    """ Transform AST to GCode"""
    
    def coord(self, axis, val):
        return (axis.value, float(val))
    
    def move(self, *items):
        # Determine if printing is needed
        has_print = items[0] == "print"
        coords = items[1:] if has_print else items
        
        # Test for parameters
        assert(same_values_unordered(coords, {'x', 'y','z', 's'}))
        
        # Create gcode command
        cmd = "G1" if has_print else "G0"
        for axis, val in coords:
            cmd += f" {axis.upper()}{val}"
        
        return cmd
        
    def pause(self):
        return "M0"
    
    def program(self, *commands):
        # remove lines only containing ""
        return "\n".join(filter(lambda c: c!= "" , [str(c) for (c) in commands]))

    '''
    Definition
    '''
    def const(self, *args):
        # TODO
        # Add ident to tab symb
        # Add value to ident
        ident, const_type, value = args
        
        print(f"Ident: {ident}")
        print(f"Type: {const_type}")
        print(f"Value: {value}")
        
        assert(check_type(value, const_type))
        
        return ""

    '''
    Control structure
    '''
    def condition(self, expr, *block):
        return flatten_str([instr for instr in block]) if expr else "" 

    
    def block(self, *block):
        return flatten_str([instr for instr in block])

    '''
    Expressions
    '''
    def expression(self, value):
        return value

    '''
    Terminals
    '''
    
    def primary(self, value):
        return value
    
    def value(self, value):
        return value
    
    def BOOLEAN(self, token):
        return token == "true"

    def NUMBER(self, value):
        return float(value)
    
    

def load_pgcode(filename):
    """Load grammar from a .pgcode"""
    pgcode = ""
    with open(f'examples/{filename}.pgcode', 'r') as file:
        pgcode = file.read()
        
    return pgcode

def load_grammar():
    """Load grammar for a .lark file"""
    grammar_file = Path(__file__).parent.parent / "grammar" / "grammar.lark"
    
    if not grammar_file.exists():
        print(f"Error: Grammar file '{grammar_file}' not found.")
        sys.exit(1)
        
    return grammar_file.read_text()

def transpile(pgcode_source):
    """Transpile le code pg-code vers G-code"""
    grammar = load_grammar()
    parser = Lark(grammar, start='program', parser='lalr')
    
    try:
        tree = parser.parse(pgcode_source)
        generator = GCodeGenerator()
        gcode = generator.transform(tree)
        
        print(f'''
----------------

TREE:
{tree.pretty()}

----------------

TRANSFORMED:
{gcode}

----------------
        ''')
        
        return gcode
    except Exception as e:
        print(f"Critical error during transpiling: {e}")
        sys.exit(1)
    
def main():
    # filename = "move_print"
    # filename = "condition"
    filename = "const"
    
    code = load_pgcode(filename)
    transpile(code)
    
    

    

if __name__ == "__main__":
    main()
