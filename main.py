from lark import Lark, Transformer, v_args
from pathlib import Path
import sys

# Define visitor
@v_args(inline=True)
class GCodeGenerator(Transformer):
    """ Transform AST to GCode"""
    
    def coord(self, axis, val):
        return (axis.value, float(val))
    
    def move(self, *coords):
        cmd = "G1"
        for axis, val in coords:
            cmd += f" {axis.upper()}{val}"
        return cmd
    
    def printc(self, state_token):
        return "M3" if state_token.value == "on" else "M5"
    
    def pause(self):
        return "M0"
    
    def start(self, *commands):
        return "\n".join(str(c) for (c) in commands)
    
    def gcode_block(self, *commands):
        return "\n".join(str(c) for (c) in commands)

    def gcommand(self, *params):
        if len(params) != 4:
            raise SyntaxError("Must have exactly 4 parameters")
        var_type = [p[0] for p in params]
        var_values = [p[1] for p in params]
        expected = {"X", "Y", "Z", "S"}
        seen = set(var_type)

        if seen != expected:
            missing = expected - seen
            extra = [v for v in var_type if var_type.count(v) > 1]
            msg = []
            if missing:
                msg.append(f"Missing: {', '.join(missing)}")
            if extra:
                msg.append(f"Duplicates: {', '.join(set(extra))}")
            raise ValueError("Invalid gcommand: " + "; ".join(msg))
        return f"G0 {" ".join([p[0] + str(p[1]) for p in params])}"
        
    def gparam_x(self, value):
        return ("X", value)
    
    def gparam_y(self, value):
        return ("Y", value)
    
    def gparam_z(self, value):
        return ("Z", value)
    
    def gparam_speed(self, value):
        return ("S", value)

def load_grammar():
    """Load grammar for a .lark file"""
    grammar_file = Path(__file__).parent / "grammar.lark"
    
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
        print(f"Erreur de transpilation: {e}")
        sys.exit(1)
    
def main():
    code = """
    G0 Y5.458 Z2.000 S8.140 X1.021
    """
    transpile(code)
    
    

    

if __name__ == "__main__":
    main()
