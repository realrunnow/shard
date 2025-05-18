import { 
  AccessModifier, Identifier, ImplDeclaration, MethodModifier, Modifiers, VarModifier,
  TypeDeclaration, ShardDeclaration, EnumDeclaration, EnumVariant, CallableDeclaration,
  CallableDefinition, VariableDeclaration, Parameter, TypeNode, BlockStatement,
  ReturnStatement, ExpressionStatement, IfStatement, IfBranch, Expression, Identifier as ASTIdentifier,
  Literal, BinaryExpression, BinaryOperator, CallExpression, InstantiationExpression,
  Program, ASTNode, Statement, Declaration
} from "../ast/nodes/nodes";
import { SourceLocation } from "../shared/meta";
import { Token } from "../tokens/token";
import { TokenTable, TokenTableVisitor } from "../tokens/token_table";
import { TokenTypes } from "../tokens/token_types";

export class Parser implements TokenTableVisitor {
  tokenTable!: TokenTable;
  program!: Program;
  // Main parser entry point
  visit(self: TokenTable): void {
    this.tokenTable = self;
    this.program = this.parseProgram(); // Parse entire program AST
  }

  // Parses identifiers like variable/type names
  // Example: "myVar" in "let myVar: i32;"
  private parseIdentifier(): Identifier {
    const token = this.tokenTable.eat(TokenTypes.IDENT);
    return new Identifier(token.value, token.sourceLocation, token.sourceLocation);
  }

  // Parses modifiers like access modifiers and flags
  // Handles: pub, priv, internal, open, const, mut, meta, pure, impure, bus, on
  // Example: "pub const" in "pub const MAX: i32 = 100;"
  private parseModifiers(): Modifiers {
    const modifiers: Modifiers = {
      access: 'internal',
    };
    while (true) {
      // Parse access modifiers
      if (this.tokenTable.peek().type === TokenTypes.PUB) {
        modifiers.access = 'pub';
        this.tokenTable.advance();
      } else if (this.tokenTable.peek().type === TokenTypes.PRIV) {
        modifiers.access = 'priv';
        this.tokenTable.advance();
      } else if (this.tokenTable.peek().type === TokenTypes.INTERNAL) {
        modifiers.access = 'internal';
        this.tokenTable.advance();
      } else if (this.tokenTable.peek().type === TokenTypes.OPEN) {
        modifiers.access = 'open';
        this.tokenTable.advance();
      
      // Parse variable flags
      } else if (this.tokenTable.peek().type === TokenTypes.CONST) {
        if (!modifiers.varFlags) modifiers.varFlags = [];
        modifiers.varFlags.push('const');
        this.tokenTable.advance();
      } else if (this.tokenTable.peek().type === TokenTypes.MUT) {
        if (!modifiers.varFlags) modifiers.varFlags = [];
        modifiers.varFlags.push('mut');
        this.tokenTable.advance();
      
      // Parse method flags
      } else if (this.tokenTable.peek().type === TokenTypes.META) {
        if (!modifiers.methodFlags) modifiers.methodFlags = [];
        modifiers.methodFlags.push('meta');
        this.tokenTable.advance();
      } else if (this.tokenTable.peek().type === TokenTypes.PURE) {
        if (!modifiers.methodFlags) modifiers.methodFlags = [];
        modifiers.methodFlags.push('pure');
        this.tokenTable.advance();
      } else if (this.tokenTable.peek().type === TokenTypes.IMPURE) {
        if (!modifiers.methodFlags) modifiers.methodFlags = [];
        modifiers.methodFlags.push('impure');
        this.tokenTable.advance();
      } else if (this.tokenTable.peek().type === TokenTypes.BUS) {
        if (!modifiers.methodFlags) modifiers.methodFlags = [];
        modifiers.methodFlags.push('bus');
        this.tokenTable.advance();
      } else if (this.tokenTable.peek().type === TokenTypes.ON) {
        if (!modifiers.methodFlags) modifiers.methodFlags = [];
        modifiers.methodFlags.push('on');
        this.tokenTable.advance();
      } else {
        break;
      }
    }
    return modifiers;
  }

  // Checks if current tokens match variable declaration start
  // Example: "x: i32" in "let x: i32;"
  private isVariableDeclarationStart(): boolean {
    const peek = this.tokenTable.peek().type;
    const peek2 = this.tokenTable.peek(2).type;
    return peek === TokenTypes.IDENT && peek2 === TokenTypes.COLON;
  }

  // Parses type annotations
  // Example: "i32" in "let x: i32;"
  private parseTypeNode(): TypeNode {
    return this.parseIdentifier();
  }

  // Parses function parameter list
  // Example: "(a: i32, b: string)"
  private parseParameters(): Parameter[] {
    this.tokenTable.eat(TokenTypes.LPAREN);
    const params: Parameter[] = [];
    while (!this.tokenTable.peekCheck(0, TokenTypes.RPAREN)) {
      const param = this.parseParameter();
      params.push(param);
      if (!this.tokenTable.peekCheck(0, TokenTypes.RPAREN)) {
        this.tokenTable.eat(TokenTypes.COMMA);
      }
    }
    this.tokenTable.eat(TokenTypes.RPAREN);
    return params;
  }

  // Parses single function parameter
  // Example: "a: i32 = 5"
  private parseParameter(): Parameter {
    const name = this.parseIdentifier();
    this.tokenTable.eat(TokenTypes.COLON);
    const typeAnnotation = this.parseTypeNode();
    let defaultValue: Expression | null = null;
    if (this.tokenTable.peek().type === TokenTypes.ASSIGN) {
      this.tokenTable.advance();
      defaultValue = this.parseExpression();
    }
    return new Parameter(
      name, typeAnnotation, defaultValue, 
      name.start, defaultValue?.end || typeAnnotation.end
    );
  }

  // Parses return type annotation
  // Example: "-> string" in "fn get(): string"
  private parseReturnType(): TypeNode | null {
    if (this.tokenTable.peek().type === TokenTypes.ARROW) {
      this.tokenTable.advance();
      return this.parseTypeNode();
    }
    return null;
  }

  // Parses block statements with braces
  // Example: "{ x = 5; return x; }"
  private parseBlockStatement(): BlockStatement {
    this.tokenTable.eat(TokenTypes.LBRACE);
    const statements: Statement[] = [];
    while (!this.tokenTable.peekCheck(0, TokenTypes.RBRACE)) {
      statements.push(this.parseStatement());
    }
    this.tokenTable.eat(TokenTypes.RBRACE);
    return new BlockStatement(statements, 
      statements[0]?.start || this.tokenTable.getPreviousSourceLocation(),
      this.tokenTable.getPreviousSourceLocation()
    );
  }

  // Main statement parser with multiple variants
  private parseStatement(): Statement {
    // Handle return statements
    if (this.tokenTable.peek().type === TokenTypes.RETURN) {
      return this.parseReturnStatement();
    
    // Handle block statements
    } else if (this.tokenTable.peek().type === TokenTypes.LBRACE) {
      return this.parseBlockStatement();
    
    // Handle if statements
    } else if (this.tokenTable.peek().type === TokenTypes.IF) {
      return this.parseIfStatement();
    
    // Handle expressions
    } else {
      const expr = this.parseExpression();
      return new ExpressionStatement(expr, expr.start, expr.end);
    }
  }

  // Parses return statements
  // Example: "return x + 5;"
  private parseReturnStatement(): ReturnStatement {
    const token = this.tokenTable.eat(TokenTypes.RETURN);
    let value: Expression | null = null;
    if (!this.tokenTable.peekCheck(0, TokenTypes.EOL)) {
      value = this.parseExpression();
    }
    this.tokenTable.eat(TokenTypes.EOL);
    return new ReturnStatement(
      value, 
      token.sourceLocation, 
      value?.end || token.sourceLocation
    );
  }

  // Detects if current token is start of if statement
  private isIfStart(): boolean {
    return this.tokenTable.peek().type === TokenTypes.IF;
  }

  // Parses if/else statements
  // Example: "if (x > 0) { ... } else { ... }"
  private parseIfStatement(): IfStatement {
    const branches: IfBranch[] = [];
    this.tokenTable.eat(TokenTypes.IF);
    this.tokenTable.eat(TokenTypes.LPAREN);
    const condition = this.parseExpression();
    this.tokenTable.eat(TokenTypes.RPAREN);
    const thenBlock = this.parseBlockStatement();
    branches.push(new IfBranch(condition, thenBlock));
    
    // Handle else/elif branches
    while (this.tokenTable.peek().type === TokenTypes.ELSE) {
      this.tokenTable.advance();
      if (this.tokenTable.peek().type === TokenTypes.IF) {
        // elif branch
        this.tokenTable.advance();
        this.tokenTable.eat(TokenTypes.LPAREN);
        const elifCondition = this.parseExpression();
        this.tokenTable.eat(TokenTypes.RPAREN);
        const elifBlock = this.parseBlockStatement();
        branches.push(new IfBranch(elifCondition, elifBlock));
      } else {
        // else branch
        const elseBlock = this.parseBlockStatement();
        branches.push(new IfBranch(null, elseBlock));
      }
    }
    return new IfStatement(
      branches, 
      branches[0].block.start, 
      branches[branches.length - 1].block.end
    );
  }

  // Main expression parser
  private parseExpression(): Expression {
    return this.parseBinaryExpression();
  }

  // Parses binary operations with operator precedence
  private parseBinaryExpression(): Expression {
    let left = this.parseAssignmentExpression();
    while (this.isBinaryOperator(this.tokenTable.peek().type)) {
      const operator = this.consumeBinaryOperator();
      const right = this.parseAssignmentExpression();
      left = new BinaryExpression(left, operator, right, left.start, right.end);
    }
    return left;
  }

  // Parses assignment expressions
  private parseAssignmentExpression(): Expression {
    const left = this.parsePrimaryExpression();
    if (this.tokenTable.peek().type === TokenTypes.ASSIGN) {
      this.tokenTable.advance();
      const right = this.parseBinaryExpression();
      return new BinaryExpression(left, BinaryOperator.Assign, right, left.start, right.end);
    }
    return left;
  }

  // Checks if token is a binary operator
  private isBinaryOperator(type: TokenTypes): boolean {
    return [
      TokenTypes.PLUS, TokenTypes.MINUS, TokenTypes.MULTIPLY, TokenTypes.DIVIDE,
      TokenTypes.EQ, TokenTypes.NE, TokenTypes.LT, TokenTypes.GT,
      TokenTypes.AND, TokenTypes.OR
    ].includes(type);
  }

  // Converts token to binary operator enum
  private consumeBinaryOperator(): BinaryOperator {
    const token = this.tokenTable.eatCurrentToken();
    switch(token.type) {
      case TokenTypes.PLUS: return BinaryOperator.Add;
      case TokenTypes.MINUS: return BinaryOperator.Subtract;
      case TokenTypes.MULTIPLY: return BinaryOperator.Multiply;
      case TokenTypes.DIVIDE: return BinaryOperator.Divide;
      case TokenTypes.EQ: return BinaryOperator.Equals;
      case TokenTypes.NE: return BinaryOperator.NotEquals;
      case TokenTypes.LT: return BinaryOperator.LessThan;
      case TokenTypes.GT: return BinaryOperator.GreaterThan;
      case TokenTypes.AND: return BinaryOperator.And;
      case TokenTypes.OR: return BinaryOperator.Or;
      default: throw new Error("Unknown binary operator");
    }
  }

  // Parses primary expressions (literals, identifiers, groups)
  private parsePrimaryExpression(): Expression {
    const token = this.tokenTable.peek();
    switch (token.type) {
      case TokenTypes.INTEGER:
      case TokenTypes.FLOAT:
        return this.parseLiteral();
      case TokenTypes.STRING:
      case TokenTypes.BOOL:
        return this.parseLiteral();
      case TokenTypes.IDENT:
        return this.parseIdentifierExpression();
      case TokenTypes.LPAREN:
        return this.parseGroupExpression();
      default:
        throw new Error(`Unexpected token in expression: ${token.toString()}`);
    }
  }

  // Parses literal values
  // Example: "42", "true", "\"hello\""
  private parseLiteral(): Literal {
    const token = this.tokenTable.eatCurrentToken();
    let value: any = null;
    switch (token.type) {
      case TokenTypes.INTEGER:
      case TokenTypes.FLOAT:
        value = parseFloat(token.value);
        break;
      case TokenTypes.STRING:
        value = token.value;
        break;
      case TokenTypes.BOOL:
        value = token.value === 'true';
        break;
    }
    return new Literal(value, token.sourceLocation, token.sourceLocation);
  }

  // Parses identifier expressions with possible calls
  // Example: "myFunc()" or just "myVar"
  private parseIdentifierExpression(): Expression {
    const ident = this.parseIdentifier();
    if (this.tokenTable.peek().type === TokenTypes.LPAREN) {
      const { args, end } = this.parseArguments();
      return new CallExpression(ident, args, ident.start, end);
    }
    return ident;
  }

  // Parses function call arguments
  // Example: "(arg1, arg2)"
  private parseArguments(): { args: Expression[], end: SourceLocation } {
    this.tokenTable.eat(TokenTypes.LPAREN);
    const args: Expression[] = [];
    while (!this.tokenTable.peekCheck(0, TokenTypes.RPAREN)) {
      args.push(this.parseExpression());
      if (!this.tokenTable.peekCheck(0, TokenTypes.RPAREN)) {
        this.tokenTable.eat(TokenTypes.COMMA);
      }
    }
    const rParenToken = this.tokenTable.eat(TokenTypes.RPAREN);
    return { args, end: rParenToken.sourceLocation };
  }

  // Parses parenthesized expressions
  // Example: "(x + 5)"
  private parseGroupExpression(): Expression {
    this.tokenTable.eat(TokenTypes.LPAREN);
    const expr = this.parseExpression();
    this.tokenTable.eat(TokenTypes.RPAREN);
    return expr;
  }

  // Parses component instantiation
  // Example: "Component(x: 5, y: 10) as myComp"
  private parseInstantiationExpression(): InstantiationExpression {
    const component = this.parseIdentifier();
    this.tokenTable.eat(TokenTypes.LPAREN);
    const args: Record<string, Expression> = {};
    while (!this.tokenTable.peekCheck(0, TokenTypes.RPAREN)) {
      const key = this.parseIdentifier();
      this.tokenTable.eat(TokenTypes.ASSIGN);
      const value = this.parseExpression();
      args[key.name] = value;
      if (!this.tokenTable.peekCheck(0, TokenTypes.RPAREN)) {
        this.tokenTable.eat(TokenTypes.COMMA);
      }
    }
    this.tokenTable.eat(TokenTypes.RPAREN);
    let alias: Identifier | null = null;
    if (this.tokenTable.peek().type === TokenTypes.AS) {
      this.tokenTable.advance();
      alias = this.parseIdentifier();
    }
    return new InstantiationExpression(
      component, args, alias, 
      component.start, alias?.end || component.end
    );
  }

  // Checks if current token is instantiation start
  private isInstantiationStart(): boolean {
    return this.tokenTable.peek().type === TokenTypes.IDENT &&
           this.tokenTable.peek(1).type === TokenTypes.LPAREN;
  }

  // Checks if current token is callable start
  private isCallableStart(): boolean {
    return this.tokenTable.peek().type === TokenTypes.IDENT &&
           this.tokenTable.peek(1).type === TokenTypes.LPAREN;
  }

  // Parses variable declarations
  // Example: "x: i32 = 5;"
  private parseVariableDeclaration(modifiers: Modifiers): VariableDeclaration {
    const name = this.parseIdentifier();
    this.tokenTable.eat(TokenTypes.COLON);
    const typeAnnotation = this.parseTypeNode();
    let initializer: Expression | null = null;
    if (this.tokenTable.peek().type === TokenTypes.ASSIGN) {
      this.tokenTable.advance();
      initializer = this.parseExpression();
    }
    this.tokenTable.eat(TokenTypes.EOL);
    return new VariableDeclaration(
      name, modifiers, typeAnnotation, initializer,
      name.start, this.tokenTable.getPreviousSourceLocation()
    );
  }

  // Parses callable definitions (functions/methods)
  // Example: "fn myFunc(a: i32): i32 { return a + 1; }"
  private parseCallableDefinition(modifiers: Modifiers): CallableDefinition {
    const name = this.parseIdentifier();
    const params = this.parseParameters();
    const returnType = this.parseReturnType();
    const body = this.parseBlockStatement();
    return new CallableDefinition(
      name, modifiers, params, returnType, body,
      name.start, body.end
    );
  }

  // FIXED
  // Parses type declarations
  // Example: "type MyType { x: i32; fn new(); }"
  private parseType(modifiers: Modifiers): TypeDeclaration {
    console.log("eating type")
    const typeToken = this.tokenTable.eat(TokenTypes.TYPE);
    console.log("eating identifier")
    const name = this.parseIdentifier();
  
    console.log("eating lbrace")
    this.tokenTable.eat(TokenTypes.LBRACE);
  
    const members: (VariableDeclaration | CallableDeclaration)[] = [];
  
    // Keep parsing until we hit RBRACE
    let foundRbrace = false;
    while (!foundRbrace) {
      console.log("eating modifiers")
      const memberModifiers = this.parseModifiers();
  
      if (this.isVariableDeclarationStart()) {
        const variable = this.parseVariableDeclaration(memberModifiers);
        members.push(variable);
      } else if (this.isCallableStart()) {
        const method = this.parseCallableDefinition(memberModifiers);
        members.push(method);
      } else if (this.tokenTable.peekCheck(0,TokenTypes.RBRACE)) {
        foundRbrace = true;
        break;
      } else {
        throw new Error("Unexpected token: " + this.tokenTable.peek().toString());
      }
    }

    console.log("eating rbrace")
    this.tokenTable.eat(TokenTypes.RBRACE);

    return new TypeDeclaration(
      name,
      modifiers,
      members,
      typeToken.sourceLocation,
      this.tokenTable.getPreviousSourceLocation()
    );
  }

  // Parses shard declarations
  // Example: "shard MyShard { x: i32; }"
  private parseShard(modifiers: Modifiers): ShardDeclaration {
    const shardToken = this.tokenTable.eat(TokenTypes.SHARD);
    const name = this.parseIdentifier();
    this.tokenTable.eat(TokenTypes.LBRACE);
    const members: (VariableDeclaration | CallableDeclaration)[] = [];
    
    // Parse shard members
    while (!this.tokenTable.peekCheck(0, TokenTypes.RBRACE)) {
      // Skip comments and EOL
      while (
        this.tokenTable.peek().type === TokenTypes.EOL ||
        this.tokenTable.peek().type === TokenTypes.COMMENT
      ) {
        this.tokenTable.advance();
      }
      if (this.tokenTable.peekCheck(0, TokenTypes.RBRACE)) break;
      
      const memberModifiers = this.parseModifiers();
      if (this.isVariableDeclarationStart()) {
        const variable = this.parseVariableDeclaration(memberModifiers);
        members.push(variable);
      } else {
        const method = this.parseCallableDefinition(memberModifiers);
        members.push(method);
      }
    }
    this.tokenTable.eat(TokenTypes.RBRACE);
    return new ShardDeclaration(
      name,
      modifiers,
      members,
      shardToken.sourceLocation,
      this.tokenTable.getPreviousSourceLocation()
    );
  }

  // Parses implementation declarations
  // Example: "impl MyImpl for MyType { fn method() { ... } }"
  private parseImpl(modifiers: Modifiers): ImplDeclaration {
    const implToken = this.tokenTable.eat(TokenTypes.IMPL);
    const target = this.parseIdentifier();
    this.tokenTable.eat(TokenTypes.FOR);
    const forType = this.parseIdentifier();
    this.tokenTable.eat(TokenTypes.LBRACE);
    const members: CallableDefinition[] = [];
    
    // Parse implementation methods
    while (!this.tokenTable.peekCheck(0, TokenTypes.RBRACE)) {
      const memberModifiers = this.parseModifiers();
      const callable = this.parseCallableDefinition(memberModifiers);
      members.push(callable);
    }
    this.tokenTable.eat(TokenTypes.RBRACE);
    return new ImplDeclaration(
      target, forType, modifiers, members, 
      implToken.sourceLocation, this.tokenTable.getPreviousSourceLocation()
    );
  }

  // Parses enum declarations
  // Example: "enum Color { Red, Green, Blue = 255 }"
  private parseEnum(modifiers: Modifiers): EnumDeclaration {
    const enumToken = this.tokenTable.eat(TokenTypes.ENUM);
    const name = this.parseIdentifier();
    this.tokenTable.eat(TokenTypes.LBRACE);
    const variants: EnumVariant[] = [];
    
    // Parse enum variants
    while (!this.tokenTable.peekCheck(0, TokenTypes.RBRACE)) {
      const variantName = this.parseIdentifier();
      let value: Expression | null = null;
      if (this.tokenTable.peek().type === TokenTypes.ASSIGN) {
        this.tokenTable.advance();
        value = this.parseExpression();
      }
      variants.push(new EnumVariant(variantName, value));
      if (!this.tokenTable.peekCheck(0, TokenTypes.RBRACE)) {
        this.tokenTable.eat(TokenTypes.COMMA);
      }
    }
    this.tokenTable.eat(TokenTypes.RBRACE);
    return new EnumDeclaration(
      name, modifiers, variants, 
      enumToken.sourceLocation, this.tokenTable.getPreviousSourceLocation()
    );
  }


  // FIXED
  // Main program parser
  private parseProgram(): Program {

    const body: Declaration[] = [];
    
    // Parse top-level declarations until EOF
    while (!this.tokenTable.peekCheck(1, TokenTypes.EOF)) {

      const modifiers = this.parseModifiers();

      let declaration: Declaration | null = null;
      
      // Determine declaration type
      if (this.tokenTable.peek().type === TokenTypes.TYPE) {
        declaration = this.parseType(modifiers);

      } else if (this.tokenTable.peek().type === TokenTypes.SHARD) {
        declaration = this.parseShard(modifiers);

      } else if (this.tokenTable.peek().type === TokenTypes.IMPL) {
        declaration = this.parseImpl(modifiers);

      } else if (this.tokenTable.peek().type === TokenTypes.ENUM) {
        declaration = this.parseEnum(modifiers);

      } else if (this.isCallableStart()) {
        declaration = this.parseCallableDefinition(modifiers);
      } else {
        throw new Error(`Unexpected token in program: ${this.tokenTable.peek().toString()}`);
      }

      if (declaration) {
        body.push(declaration);
      }
    }
    
    // Create program node with source locations
    const startLoc = body.length > 0 
      ? body[0].start 
      : { line: 0, column: 0, offset: 0, file: "" };
    const endLoc = this.tokenTable.getPreviousSourceLocation();
    return new Program(body, startLoc, endLoc);
  }
}