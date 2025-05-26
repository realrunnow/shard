import { serializeIndented } from "./ast/encoders/compact";
import { serialize } from "./ast/encoders/json";
import {
  ASTNode,
  BinaryExpression,
  BinaryOperator,
  BlockStatement,
  CallableDeclaration,
  CallableDefinition,
  ConditionalExpression,
  EnumDeclaration,
  Expression,
  ExpressionStatement,
  FunctionCallExpression,
  Identifier,
  IfStatement,
  ImplDeclaration,
  Literal,
  Modifiers,
  Program,
  ShardDeclaration,
  TypeDeclaration,
  TypeIdentifier,
  UnaryExpression,
  UnaryOperator,
  VariableDeclaration,
  WhileStatement,
} from "./ast/nodes/nodes";
import { Lexer } from "./lexer/lexer";
import { Parser } from "./parser/parser";
import { SourceLocation } from "./shared/meta";
import { TokenTable } from "./tokens/token_table";

import * as fs from "fs";
import * as path from "path";

// Ensure logs folder exists
const logDir = path.join(__dirname, "logs");
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir);
}

var text = `
// === Imports ===
// import core.math
// import system.utils as ut

// === Enum with values ===
enum Mode {
  Start = 0;
  Run = 1;
  Stop = 2;
}

// === Type with all modifiers and abstract methods ===
type Engine {
  pub id: int;
  priv name: string;
  internal status: bool = true;
  open config: string = "none";
  const PI: float = 3.14;

  init(name: string);
  pure statusMessage(code: int) -> string;
  impure evaluate(mode: Mode);
  impure loopCounter(max: int);
  pure logicCheck(a: int, b: int) -> bool;
  impure mathOps(x: float, y: float) -> float;
  on error(message: string);
  bus transmit(data: string);
}

// === Shard component with abstract methods ===
shard Display {
  pub text: string;
  mut brightness: int = 5;
  internal ready: bool = false;

  meta init();
  bus broadcast(signal: string);
  on update();
  impure toggle(state: bool);
}

// === Another shard covering all visibility and modifiers ===
shard Modifiers {
  pub count: int;
  priv flag: bool;
  internal state: string;
  open message: string = "Open";
  const LIMIT: int = 100;
  mut step: int = 1;

  meta init();
  on trigger();
  bus pulse();
}

// === Implementation block for Engine type ===
impl Engine {
  meta calibrate() {
    print("Engine calibrated");
  }

  impure reset() {
    id = 0;
    name = "reset";
  }

  impure init(name: string) {
    print("Engine initialized: " + name);
  }

  pure statusMessage(code: int) -> string {
    return code == 0 ? "Ready" : "Error";
  }

  impure evaluate(mode: Mode) {
    if (mode == Mode.Start) {
      print("Start");
    } elif (mode == Mode.Run) {
      print("Run");
    } else {
      print("Stop");
    }
  }

  impure loopCounter(max: int) {
    i: int = 0;
    while (i < max) {
      i += 1;
      print(i);
    }
  }

  pure logicCheck(a: int, b: int) -> bool {
    return (a > b and b != 0) or (a < 0 || b < 0);
  }

  impure mathOps(x: float, y: float) -> float {
    x *= 2;
    y /= 3;
    return x + y - PI;
  }

  on error(message: string) {
    print("Error: " + message);
  }

  bus transmit(data: string) {
    print("Transmitting: " + data);
  }
}

// === Implementation block for Display shard ===
impl Display {
  meta init() {
    text = "Hello";
    brightness = 10;
  }

  bus broadcast(signal: string) {
    print("Broadcasting: " + signal);
  }

  on update() {
    print("Display updated");
  }

  impure toggle(state: bool) {
    ready = !state;
  }
}

// === Implementation block for Modifiers shard ===
impl Modifiers {
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

// === Implementation block for Display methods on Engine type ===
impl Display for Engine {
  meta connect() {
    ready = true;
    print("Connected display");
  }

  impure showData(value: int) {
    print("Value: " + value);
  }
}

// === Function with full expression tests ===
pure process(data: string, active: bool = true) -> int {
  score: int = active ? 100 : 0;
  score += data == "pass" ? 50 : -50;
  return score;
}

// === Component instantiation ===
// Engine("Main") as mainEngine;
// Display(text = "Init", brightness = 3) as mainDisplay;
// Modifiers() as modShard;
`;

var tokens = new TokenTable();
var lexer = new Lexer(text);

tokens.accept(lexer);

const pad = (str: string, len: number) => str.padEnd(len, " ");
const tokenHeader =
  "| " +
  pad("Type", 10) +
  "| " +
  pad("Value", 20) +
  "| " +
  pad("Line", 6) +
  "| " +
  pad("Column", 8) +
  "| File";

const tokenLines: string[] = [tokenHeader];
for (const token of tokens.getTokens()) {
  tokenLines.push(token.toString());
}

// Write tokens to file
fs.writeFileSync(path.join(logDir, "latest_tokens.txt"), tokenLines.join("\n"));

var parser = new Parser();
tokens.accept(parser);

// Serialize and write AST to file
const astOutput = serializeIndented(parser.program);
fs.writeFileSync(path.join(logDir, "latest_ast.txt"), astOutput);

const astOutputJSON = serialize(parser.program);
fs.writeFileSync(path.join(logDir, "latest_ast.json"), astOutputJSON);

// Also print AST to console
console.log(astOutput);
