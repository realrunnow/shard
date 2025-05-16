import { SourceLocation } from "../../shared/meta";
  
export abstract class ASTNode {
  constructor(
    public start: SourceLocation,
    public end: SourceLocation
  ) {}
}

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
    public forType: Identifier,
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
    public typeAnnotation: TypeNode | null,
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

export class IfBranch {
  constructor(
    public condition: Expression | null, // null = else
    public block: BlockStatement
  ) {}
}

// === Expressions ===

export abstract class Expression extends ASTNode {}

export class Identifier extends Expression {
  constructor(
    public name: string,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

export class Literal extends Expression {
  constructor(
    public value: string | number | boolean | null,
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

export enum BinaryOperator {
  Add = '+',
  Subtract = '-',
  Multiply = '*',
  Divide = '/',
  Equals = '==',
  NotEquals = '!=',
  LessThan = '<',
  GreaterThan = '>',
  And = '&&',
  Or = '||',
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

export class CallExpression extends Expression {
  constructor(
    public callee: Expression,
    public args: Expression[],
    start: SourceLocation,
    end: SourceLocation
  ) {
    super(start, end);
  }
}

// Component(step = 5) as myCounter;
export class InstantiationExpression extends Expression {
  constructor(
    public component: Identifier,
    public args: Record<string, Expression>,
    public alias: Identifier | null,
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
