import { serializeIndented } from "./ast/encoders/compact";
import { serialize } from "./ast/encoders/json";
import { ASTNode, BinaryExpression, BinaryOperator, BlockStatement, CallableDeclaration, CallableDefinition, ConditionalExpression, EnumDeclaration, Expression, ExpressionStatement, FunctionCallExpression, Identifier, IfStatement, ImplDeclaration, Literal, Modifiers, Program, ShardDeclaration, TypeDeclaration, TypeIdentifier, UnaryExpression, UnaryOperator, VariableDeclaration, WhileStatement } from "./ast/nodes/nodes"
import { Lexer } from "./lexer/lexer"
import { Parser } from "./parser/parser"
import { SourceLocation } from "./shared/meta";
import { TokenTable } from "./tokens/token_table"








var text = `// Complex test file for the Shard parser
// Tests all the parser features we've fixed

// Type with empty parameter functions, typed fields and string literals
type TestType {
  // Empty parameter function
  init() {
    print("Constructor");
  }
  
  // Fields with type annotations
  x: int;
  y: float;
  message: string;
  
  // Method with parameters and return type
  calculate(a: int, b: float = 1.0) -> float {
    return a + b;
  }
}

// Shard component definition
shard Counter {
  pub count: int;
  pub step: int = 1;
  
  // Methods
  increment() {
    count = count + step;
  }
  
  reset() {
    count = 0;
  }
}

// Implementation block
impl Counter for TestType {
  meta init() {
    count = 0;
    step = 2;
    print("Counter initialized");
  }
  
  // Method with empty parameter list
  getCount() -> int {
    return count;
  }
}

// Standalone function with complex parameter
process(data: string, options: bool = true) -> int {
  print("Processing: " + data);
  return 42;
}

// Component instantiation at top level
Counter(step = 5) as myCounter;

// Another component instantiation
TestType() as myTest;

/* Long comment line 1
long comment line 2
long comment line 3*/` 


var text2 = `
pub value: i32
enum DIh {
  DIH;
  DIH;

}
pub shard Ident {
  // comment
  // comment
  pub init(param:i32) -> i32
  pub value: i32
}
impl String for Ident {
  pub init(param:i32) -> i32 {
    var: bool 
    var: bool 
  }
}

`

var tokens = new TokenTable()
var lexer = new Lexer(text2)

tokens.accept(lexer)


const pad = (str: string, len: number) => str.padEnd(len, ' ');
console.log(        
"| " + pad("Type", 10) + 
"| " + pad("Value", 20) + 
"| " + pad("Line", 6) + 
"| " + pad("Column", 8) + 
"| File"
)
for(const token of tokens.getTokens()) {
    console.log(token.toString())
}

var parser = new Parser()
tokens.accept(parser)



//console.log(JSON.stringify(serialize(parser.program), null, 2));
console.log(text2);

console.log(serializeIndented(parser.program));
