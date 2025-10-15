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
        return gcode
    except Exception as e:
        print(f"Erreur de transpilation: {e}")
        sys.exit(1)
    
def main():
    code = """
    print on
    move x=1 y=2 z=3
    print off
    move z=10
    pause
    """
    print(transpile(code))
    
    

    

if __name__ == "__main__":
    main()
