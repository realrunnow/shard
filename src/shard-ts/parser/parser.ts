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

  visit(self: TokenTable): void {
    this.tokenTable = self;
    const program = this.parseProgram();
    // Optionally store or return the AST
  }

  // Helper Parsing Methods
  private parseIdentifier(): Identifier {
    const token = this.tokenTable.eat(TokenTypes.IDENT);
    return new Identifier(token.value, token.sourceLocation, token.sourceLocation);
  }

  private parseModifiers(): Modifiers {
    const modifiers: Modifiers = {
      access: 'internal',
    };
    
    while (true) {
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
      } else if (this.tokenTable.peek().type === TokenTypes.CONST) {
        if (!modifiers.varFlags) modifiers.varFlags = [];
        modifiers.varFlags.push('const');
        this.tokenTable.advance();
      } else if (this.tokenTable.peek().type === TokenTypes.MUT) {
        if (!modifiers.varFlags) modifiers.varFlags = [];
        modifiers.varFlags.push('mut');
        this.tokenTable.advance();
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

  private isVariableDeclarationStart(): boolean {
    const peek = this.tokenTable.peek().type;
    const peek2 = this.tokenTable.peek(2).type;
    return peek === TokenTypes.IDENT && peek2 === TokenTypes.COLON;
  }

  private parseTypeNode(): TypeNode {
    return this.parseIdentifier();
  }

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

  private parseReturnType(): TypeNode | null {
    if (this.tokenTable.peek().type === TokenTypes.ARROW) {
      this.tokenTable.advance();
      return this.parseTypeNode();
    }
    return null;
  }

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

  private parseStatement(): Statement {
    if (this.tokenTable.peek().type === TokenTypes.RETURN) {
      return this.parseReturnStatement();
    } else if (this.tokenTable.peek().type === TokenTypes.LBRACE) {
      return this.parseBlockStatement();
    } else if (this.tokenTable.peek().type === TokenTypes.IF) {
      return this.parseIfStatement();
    } else {
      const expr = this.parseExpression();
      this.tokenTable.eat(TokenTypes.EOL); // Only EOL required after expressions
      return new ExpressionStatement(expr, expr.start, expr.end);
    }
  }

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

  private isIfStart(): boolean {
    return this.tokenTable.peek().type === TokenTypes.IF;
  }

  private parseIfStatement(): IfStatement {
    const branches: IfBranch[] = [];
    this.tokenTable.eat(TokenTypes.IF);
    this.tokenTable.eat(TokenTypes.LPAREN);
    const condition = this.parseExpression();
    this.tokenTable.eat(TokenTypes.RPAREN);
    const thenBlock = this.parseBlockStatement();
    branches.push(new IfBranch(condition, thenBlock));
    
    while (this.tokenTable.peek().type === TokenTypes.ELSE) {
      this.tokenTable.advance();
      
      if (this.tokenTable.peek().type === TokenTypes.IF) {
        this.tokenTable.advance();
        this.tokenTable.eat(TokenTypes.LPAREN);
        const elifCondition = this.parseExpression();
        this.tokenTable.eat(TokenTypes.RPAREN);
        const elifBlock = this.parseBlockStatement();
        branches.push(new IfBranch(elifCondition, elifBlock));
      } else {
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

  private parseExpression(): Expression {
    return this.parseBinaryExpression();
  }

  private parseBinaryExpression(): Expression {
    let left = this.parseAssignmentExpression();
    
    while (this.isBinaryOperator(this.tokenTable.peek().type)) {
      const operator = this.consumeBinaryOperator();
      const right = this.parseAssignmentExpression();
      left = new BinaryExpression(left, operator, right, left.start, right.end);
    }
    
    return left;
  }

  private parseAssignmentExpression(): Expression {
    const left = this.parsePrimaryExpression();
    
    if (this.tokenTable.peek().type === TokenTypes.ASSIGN) {
      this.tokenTable.advance();
      const right = this.parseBinaryExpression();
      return new BinaryExpression(left, BinaryOperator.Assign, right, left.start, right.end);
    }
    
    return left;
  }

  private isBinaryOperator(type: TokenTypes): boolean {
    return [
      TokenTypes.PLUS, TokenTypes.MINUS, TokenTypes.MULTIPLY, TokenTypes.DIVIDE,
      TokenTypes.EQ, TokenTypes.NE, TokenTypes.LT, TokenTypes.GT,
      TokenTypes.AND, TokenTypes.OR
    ].includes(type);
  }

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
        throw new Error(`Unexpected token in expression: ${token.type}`);
    }
  }

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

  private parseIdentifierExpression(): Expression {
    const ident = this.parseIdentifier();
    
    if (this.tokenTable.peek().type === TokenTypes.LPAREN) {
      const { args, end } = this.parseArguments();
      return new CallExpression(ident, args, ident.start, end);
    }
    
    return ident;
  }

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

  private parseGroupExpression(): Expression {
    this.tokenTable.eat(TokenTypes.LPAREN);
    const expr = this.parseExpression();
    this.tokenTable.eat(TokenTypes.RPAREN);
    return expr;
  }

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

  private isInstantiationStart(): boolean {
    return this.tokenTable.peek().type === TokenTypes.IDENT &&
           this.tokenTable.peek(2).type === TokenTypes.LPAREN;
  }

  private isCallableStart(): boolean {
    return this.tokenTable.peek().type === TokenTypes.IDENT &&
           this.tokenTable.peek(2).type === TokenTypes.LPAREN;
  }

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

  private parseType(modifiers: Modifiers): TypeDeclaration {
    const typeToken = this.tokenTable.eat(TokenTypes.TYPE);
    const name = this.parseIdentifier();
    this.tokenTable.eat(TokenTypes.LBRACE);
    const members: (VariableDeclaration | CallableDeclaration)[] = [];
  
    while (!this.tokenTable.peekCheck(0, TokenTypes.RBRACE)) {
      // ✅ Skip COMMENT and EOL tokens before parsing each member
      while (
        this.tokenTable.peek().type === TokenTypes.EOL ||
        this.tokenTable.peek().type === TokenTypes.COMMENT
      ) {
        this.tokenTable.advance();
      }
  
      // Stop parsing if we hit the closing brace
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
    return new TypeDeclaration(
      name,
      modifiers,
      members,
      typeToken.sourceLocation,
      this.tokenTable.getPreviousSourceLocation()
    );
  }

  private parseShard(modifiers: Modifiers): ShardDeclaration {
    const shardToken = this.tokenTable.eat(TokenTypes.SHARD);
    const name = this.parseIdentifier();
    this.tokenTable.eat(TokenTypes.LBRACE);
    const members: (VariableDeclaration | CallableDeclaration)[] = [];
  
    while (!this.tokenTable.peekCheck(0, TokenTypes.RBRACE)) {
      // ✅ Skip COMMENT and EOL tokens
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

  private parseImpl(modifiers: Modifiers): ImplDeclaration {
    const implToken = this.tokenTable.eat(TokenTypes.IMPL);
    const target = this.parseIdentifier();
    this.tokenTable.eat(TokenTypes.FOR);
    const forType = this.parseIdentifier();
    this.tokenTable.eat(TokenTypes.LBRACE);
    const members: CallableDefinition[] = [];
    
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

  private parseEnum(modifiers: Modifiers): EnumDeclaration {
    const enumToken = this.tokenTable.eat(TokenTypes.ENUM);
    const name = this.parseIdentifier();
    this.tokenTable.eat(TokenTypes.LBRACE);
    const variants: EnumVariant[] = [];
    
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

  private parseProgram(): Program {
    const body: Declaration[] = [];
  
    while (!this.tokenTable.peekCheck(0, TokenTypes.EOF)) {
      const modifiers = this.parseModifiers();
      let decl: Declaration | null = null;
  
      // Check current token (0), not next (1)
      if (this.tokenTable.peek().type === TokenTypes.TYPE) {
        decl = this.parseType(modifiers);

      } else if (this.tokenTable.peek().type === TokenTypes.SHARD) {
        decl = this.parseShard(modifiers);

      } else if (this.tokenTable.peek().type === TokenTypes.IMPL) {
        decl = this.parseImpl(modifiers);

      } else if (this.tokenTable.peek().type === TokenTypes.ENUM) {
        decl = this.parseEnum(modifiers);

      } else if (this.isCallableStart()) {
        decl = this.parseCallableDefinition(modifiers);

      } else if (this.isInstantiationStart()) {
        const expr = this.parseInstantiationExpression();

        decl = new ExpressionStatement(expr, expr.start, expr.end) as unknown as Declaration;
      } else {
        // Unexpected token, skip it
        this.tokenTable.advance();
        continue;
      }
  
      if (decl) {
        body.push(decl);
      }
    }
  
    const startLoc = body.length > 0 
      ? body[0].start 
      : { line: 0, column: 0, offset: 0, file: "" };
    
    const endLoc = this.tokenTable.getPreviousSourceLocation();
    return new Program(body, startLoc, endLoc);
  }
}