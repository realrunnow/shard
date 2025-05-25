import { serializeIndented } from "./ast/encoders/compact";
import { serialize } from "./ast/encoders/json";
import { ASTNode, BinaryExpression, BinaryOperator, BlockStatement, CallableDeclaration, CallableDefinition, ConditionalExpression, EnumDeclaration, Expression, ExpressionStatement, FunctionCallExpression, Identifier, IfStatement, ImplDeclaration, Literal, Modifiers, Program, ShardDeclaration, TypeDeclaration, TypeIdentifier, UnaryExpression, UnaryOperator, VariableDeclaration, WhileStatement } from "./ast/nodes/nodes"
import { Lexer } from "./lexer/lexer"
import { Parser } from "./parser/parser"
import { SourceLocation } from "./shared/meta";
import { TokenTable } from "./tokens/token_table"








var text = `// === Imports ===
import core.math
import system.utils as ut

// === Enum with values ===
enum Mode {
  Start = 0;
  Run = 1;
  Stop = 2;
}

// === Type with all modifiers, logic, and methods ===
type Engine {
  pub id: int;
  priv name: string;
  internal status: bool = true;
  open config: string = "none";
  const PI: float = 3.14;

  init(name: string) {
    print("Engine initialized: " + name);
  }

  // Pure method using ternary
  pure statusMessage(code: int) -> string {
    return code == 0 ? "Ready" : "Error";
  }

  // If / elif / else
  impure evaluate(mode: Mode) {
    if (mode == Mode.Start) {
      print("Start");
    } elif (mode == Mode.Run) {
      print("Run");
    } else {
      print("Stop");
    }
  }

  // While loop with compound ops
  impure loopCounter(max: int) {
    var i: int = 0;
    while (i < max) {
      i += 1;
      print(i);
    }
  }

  // Logical expression test
  pure logicCheck(a: int, b: int) -> bool {
    return (a > b and b != 0) or (a < 0 || b < 0);
  }

  // Compound assignment, math ops
  impure mathOps(x: float, y: float) -> float {
    x *= 2;
    y /= 3;
    return x + y - PI;
  }

  // on method
  on error(message: string) {
    print("Error: " + message);
  }

  // bus method
  bus transmit(data: string) {
    print("Transmitting: " + data);
  }
}

// === Shard component ===
shard Display {
  pub text: string;
  mut brightness: int = 5;
  internal ready: bool = false;

  meta init() {
    text = "Hello";
    brightness = 10;
  }

  // Bus method
  bus broadcast(signal: string) {
    print("Broadcasting: " + signal);
  }

  // On method
  on update() {
    print("Display updated");
  }

  impure toggle(state: bool) {
    ready = !state;
  }
}

// === Impl block (same type) ===
impl Engine {
  meta calibrate() {
    print("Engine calibrated");
  }

  impure reset() {
    id = 0;
    name = "reset";
  }
}

// === Impl block (for another type) ===
impl Display for Engine {
  meta connect() {
    ready = true;
    print("Connected display");
  }

  impure showData(value: int) {
    print("Value: " + value);
  }
}

// === Another shard covering all visibility and modifiers ===
shard Modifiers {
  pub count: int;
  priv flag: bool;
  internal state: string;
  open message: string = "Open";
  const LIMIT: int = 100;
  mut step: int = 1;

  meta init() {
    count = 0;
    step = 10;
  }

  on trigger() {
    count += step;
  }

  bus pulse() {
    print("Pulse sent");
  }
}

// === Function with full expression tests ===
pure process(data: string, active: bool = true) -> int {
  var score: int = active ? 100 : 0;
  score += data == "pass" ? 50 : -50;
  return score;
}

// === Component instantiation ===
// Engine("Main") as mainEngine;
// Display(text = "Init", brightness = 3) as mainDisplay;
// Modifiers() as modShard;

`

var tokens = new TokenTable()
var lexer = new Lexer(text)

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
console.log(text);

console.log(serializeIndented(parser.program));
