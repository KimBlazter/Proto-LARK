from lark import Lark, Transformer, v_args
from pathlib import Path
import sys
from utils import same_values_unordered, flatten_str

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
    
    def start(self, *commands):
        # remove lines only containing ""
        return "\n".join(filter(lambda c: c!= "" , [str(c) for (c) in commands]))

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
    def BOOLEAN(self, token):
        return token == "true"

    def NUMBER(self, value):
        return float(value)
    
    '''def gcode_block(self, *commands):
        return "\n".join(str(c) for (c) in commands)

    def gcommand(self, *params):
        assert(same_values_unordered(params, {"X", "Y", "Z", "S"}))
        
        return f"G0 {" ".join([id + str(v) for id, v in params])}"
        
    def gparam_x(self, value):
        return ("X", value)
    
    def gparam_y(self, value):
        return ("Y", value)
    
    def gparam_z(self, value):
        return ("Z", value)
    
    def gparam_speed(self, value):
        return ("S", value)'''

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
    parser = Lark(grammar, start='start', parser='lalr')
    
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
    filename = "move_print"
    # filename = "condition"
    
    code = load_pgcode(filename)
    transpile(code)
    
    

    

if __name__ == "__main__":
    main()
