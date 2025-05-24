import { SourceLocation } from "../../shared/meta";
  
export abstract class ASTNode {
  constructor(
    public start: SourceLocation,
    public end: SourceLocation
  ) {}
}

export abstract class Expression extends ASTNode {}



// Modifiers
export type AccessModifier = 'pub' | 'priv' | 'internal' | 'open';
export type VarModifier = 'const' | 'mut';
export type MethodModifier = 'pure' | 'impure' | 'meta' | 'bus' | 'on';

export interface Modifiers {
  access: AccessModifier;
  varFlags?: VarModifier[];
  methodFlags?: MethodModifier[];
}

// === Declarations ===

export abstract class Declaration extends ASTNode {
  constructor(
    public name: Identifier,
    public modifiers: Modifiers,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

// type TestType { x: int; y: float; }
export class TypeDeclaration extends Declaration {
  constructor(
    name: Identifier,
    modifiers: Modifiers,
    public members: (VariableDeclaration | CallableDeclaration)[],
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(name, modifiers, start, end);
  }
}

// shard Counter { pub count: int; }
export class ShardDeclaration extends Declaration {
  constructor(
    name: Identifier,
    modifiers: Modifiers,
    public members: (VariableDeclaration | CallableDeclaration)[],
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(name, modifiers, start, end);
  }
}

// impl Counter for TestType { ... }
export class ImplDeclaration extends Declaration {
  constructor(
    public target: Identifier,
    public forType: Identifier | null,
    modifiers: Modifiers,
    public members: CallableDefinition[],
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(target, modifiers, start, end);
  }
}

// enum Color { Red, Green = "green" }
export class EnumDeclaration extends Declaration {
  constructor(
    name: Identifier,
    modifiers: Modifiers,
    public variants: EnumVariant[],
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(name, modifiers, start, end);
  }
}

export class EnumVariant {
  constructor(
    public name: Identifier,
    public value: Expression | null
  ) {}
}

// process(data: string) -> int { return 42; }
export class CallableDeclaration extends Declaration {
  constructor(
    name: Identifier,
    modifiers: Modifiers,
    public params: Parameter[],
    public returnType: TypeNode | null,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(name, modifiers, start, end);
  }
}

// process(data: string) -> int { return 42; }
export class CallableDefinition extends CallableDeclaration {
  constructor(
      name: Identifier,
      modifiers: Modifiers,
      public params: Parameter[],
      public returnType: TypeNode | null,
      public body: BlockStatement,
      start: SourceLocation,
      end: SourceLocation
  ) {
      super(name, modifiers, params, returnType, start, end);
  }
}
// pub step: int = 1;
export class VariableDeclaration extends Declaration {
  constructor(
    name: Identifier,
    modifiers: Modifiers,
    public typeAnnotation: TypeNode | null,
    public initializer: Expression | null,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(name, modifiers, start, end);
  }
}

// === Parameters ===

export class Parameter {
  constructor(
    public name: Identifier,
    public typeAnnotation: TypeIdentifier | null,
    public defaultValue: Expression | null,
    public start: SourceLocation,
    public end: SourceLocation
  ) {}
}

// === Types ===

export type TypeNode = Identifier; // Extend with generic types later

// === Statements ===

export abstract class Statement extends ASTNode {}

export class BlockStatement extends Statement {
  constructor(
    public statements: Statement[],
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

// return count;
export class ReturnStatement extends Statement {
  constructor(
    public value: Expression | null,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

// count = count + step;
export class ExpressionStatement extends Statement {
  constructor(
    public expression: Expression,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

// if (...) {...} else if (...) {...} else {...}
export class IfStatement extends Statement {
  constructor(
    public branches: IfBranch[],
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}



export class IfBranch extends Statement {
  constructor(
    public condition: Expression | null, // null = else
    public block: BlockStatement,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

export class WhileStatement extends Statement {
  constructor(
    public condition: Expression,
    public block: BlockStatement,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

export class ForStatement extends Statement {
  constructor(
    public variable: Identifier,
    public iterable: Expression,
    public block: BlockStatement,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}






// === Expressions ===


export class Identifier extends Expression {
  constructor(
    public name: string,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

export class TypeIdentifier extends Identifier {
  constructor(
    public name: string,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(name, start, end);
  }
}


export enum UnaryOperator {
  Negate,
  Not,
  IncPrefix,
  DecPrefix,
  IncPostfix,
  DecPostfix
}

export enum BinaryOperator {
  Add,
  Subtract,
  Multiply,
  Divide,
  Modulo,
  Power,
  Equals,
  NotEquals,
  LessThan,
  GreaterThan,
  LessThanOrEqual,
  GreaterThanOrEqual,
  And,
  Or,
  Assign,
  AddAssign,
  SubtractAssign,
  MultiplyAssign,
  DivideAssign
}

export class Literal extends Expression {
  constructor(public value: number | string | boolean, start: SourceLocation, end: SourceLocation) {
    super(start, end);
  }
}

export class UnaryExpression extends Expression {
  constructor(
    public operator: UnaryOperator,
    public operand: Expression,
    public isPostfix: boolean = false,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

export class BinaryExpression extends Expression {
  constructor(
    public left: Expression,
    public operator: BinaryOperator,
    public right: Expression,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

export class ConditionalExpression extends Expression {
  constructor(
    public condition: Expression,
    public thenBranch: Expression,
    public elseBranch: Expression,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

export class CallParameter extends Expression { 
  constructor(
    public name: Identifier,
    public value: Expression,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

export class FunctionCallExpression extends Expression {
  constructor(
    public name: Identifier,
    public args: Expression[],
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

// === Top-Level AST ===

export class Program extends ASTNode {
  constructor(
    public body: Declaration[],
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}
