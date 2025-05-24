import { 
  AccessModifier, Identifier, ImplDeclaration, MethodModifier, Modifiers, VarModifier,
  TypeDeclaration, ShardDeclaration, EnumDeclaration, EnumVariant, CallableDeclaration,
  CallableDefinition, VariableDeclaration, Parameter, TypeNode, BlockStatement,
  ReturnStatement, ExpressionStatement, IfStatement, IfBranch, Expression, Identifier as ASTIdentifier,
  Literal, BinaryExpression, BinaryOperator, 
  Program, ASTNode, Statement, Declaration,
  TypeIdentifier,
  WhileStatement,
  CallParameter,
  UnaryExpression,
  UnaryOperator,
  ConditionalExpression,
  FunctionCallExpression
} from "../ast/nodes/nodes";
import { SourceLocation } from "../shared/meta";
import { Token } from "../tokens/token";
import { TokenTable, TokenTableVisitor } from "../tokens/token_table";
import { TokenTypes } from "../tokens/token_types";

export class Parser implements TokenTableVisitor {
  tokenTable!: TokenTable;
  program!: Program;

  // ─────────────────────────────────────────────────────────────────────────────
  // SECTION Commonly used methods
  // ─────────────────────────────────────────────────────────────────────

  // Parses variable and function identifiers 
  // "myVar" in "myVar: i32;"
  // REVIEW Ident parser
  private parseIdentifier(): Identifier {
    const token = this.tokenTable.eat(TokenTypes.IDENT);
    return new Identifier(token.value, token.sourceLocation, token.sourceLocation);
  }

  // Parses type identifiers
  // "i32" in "myVar: i32;"
  // REVIEW Type ident parser
  private parseTypeIdentifier(): TypeIdentifier {
    const token = this.tokenTable.eat(TokenTypes.IDENT);
    return new TypeIdentifier(token.value, token.sourceLocation, token.sourceLocation);
  }

  private isModifier() : boolean { 
    return [
      TokenTypes.PUB, TokenTypes.PRIV, TokenTypes.INTERNAL, TokenTypes.OPEN,
      TokenTypes.CONST, TokenTypes.MUT, TokenTypes.META, TokenTypes.PURE,
      TokenTypes.IMPURE, TokenTypes.BUS, TokenTypes.ON
    ].includes(this.tokenTable.peek().type);
  }

  // Parses modifiers like access modifiers and flags
  // Handles: pub, priv, internal, open, const, mut, meta, pure, impure, bus, on
  // Example: "pub const" in "pub const MAX: i32 = 100;"
  // REVIEW Modifier parser
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
  //!SECTION 




  // ─────────────────────────────────────────────────────────────────────────────
  // SECTION Expression parsing
  // ─────────────────────────────────────────────────────────────────────────────

  // TODO: Operator check
  // Checks if token is a binary operator
 // Updated token checks use peekCheck(offset, type)
private isBinaryOperator(): boolean {
  return [
    TokenTypes.PLUS, TokenTypes.MINUS, TokenTypes.MULTIPLY, TokenTypes.DIVIDE,
    TokenTypes.MODULO, TokenTypes.EXPONENT,
    TokenTypes.EQ, TokenTypes.NE, TokenTypes.LT, TokenTypes.GT,
    TokenTypes.AND, TokenTypes.OR
  ].some(type => this.tokenTable.peekCheck(0, type));
}

private consumeBinaryOperator(): BinaryOperator {
  const token = this.tokenTable.eatCurrentToken(); // eatCurrentToken() is valid for known binary ops
  switch(token.type) {
    case TokenTypes.PLUS: return BinaryOperator.Add;
    case TokenTypes.MINUS: return BinaryOperator.Subtract;
    case TokenTypes.MULTIPLY: return BinaryOperator.Multiply;
    case TokenTypes.DIVIDE: return BinaryOperator.Divide;
    case TokenTypes.MODULO: return BinaryOperator.Modulo;
    case TokenTypes.EXPONENT: return BinaryOperator.Power;
    case TokenTypes.EQ: return BinaryOperator.Equals;
    case TokenTypes.NE: return BinaryOperator.NotEquals;
    case TokenTypes.LT: return BinaryOperator.LessThan;
    case TokenTypes.GT: return BinaryOperator.GreaterThan;
    case TokenTypes.AND: return BinaryOperator.And;
    case TokenTypes.OR: return BinaryOperator.Or;
    default: throw new Error(`Unknown binary operator: ${token.type}`);
  }
}

private parseExpression(): Expression {
  return this.parseAssignment();
}

private parseAssignment(): Expression {
  const left = this.parseConditional();
  
  if (this.tokenTable.peekCheck(0, TokenTypes.EQ)) { // Uses peekCheck instead of direct type comparison
    const op = this.consumeBinaryOperator(); // Will consume '='
    const right = this.parseAssignment();
    return new BinaryExpression(left, op, right, left.start, right.end);
  }
  
  return left;
}

private parseConditional(): Expression {
  const expr = this.parseLogicalOr();
  
  if (this.tokenTable.peekCheck(0, TokenTypes.QUESTION_MARK)) {
    this.tokenTable.eat(TokenTypes.QUESTION_MARK); // Uses explicit eat()
    const thenBranch = this.parseExpression();
    this.tokenTable.eat(TokenTypes.COLON);
    const elseBranch = this.parseConditional();
    return new ConditionalExpression(
      expr, thenBranch, elseBranch, 
      expr.start, elseBranch.end
    );
  }
  
  return expr;
}

private parseLogicalOr(): Expression {
  let left = this.parseLogicalAnd();
  
  while (this.tokenTable.peekCheck(0, TokenTypes.OR)) {
    const op = this.consumeBinaryOperator();
    const right = this.parseLogicalAnd();
    left = new BinaryExpression(left, op, right, left.start, right.end);
  }
  
  return left;
}

private parseLogicalAnd(): Expression {
  let left = this.parseEquality();
  
  while (this.tokenTable.peekCheck(0, TokenTypes.AND)) {
    const op = this.consumeBinaryOperator();
    const right = this.parseEquality();
    left = new BinaryExpression(left, op, right, left.start, right.end);
  }
  
  return left;
}

private parseEquality(): Expression {
  let left = this.parseRelational();
  
  while (this.tokenTable.peekCheck(0, TokenTypes.EQ) || 
         this.tokenTable.peekCheck(0, TokenTypes.NE)) {
    const op = this.consumeBinaryOperator();
    const right = this.parseRelational();
    left = new BinaryExpression(left, op, right, left.start, right.end);
  }
  
  return left;
}

private parseRelational(): Expression {
  let left = this.parseAdditive();
  
  while (this.tokenTable.peekCheck(0, TokenTypes.LT) ||
         this.tokenTable.peekCheck(0, TokenTypes.GT)) {
    const op = this.consumeBinaryOperator();
    const right = this.parseAdditive();
    left = new BinaryExpression(left, op, right, left.start, right.end);
  }
  
  return left;
}

private parseAdditive(): Expression {
  let left = this.parseMultiplicative();
  
  while (this.tokenTable.peekCheck(0, TokenTypes.PLUS) || 
         this.tokenTable.peekCheck(0, TokenTypes.MINUS)) {
    const op = this.consumeBinaryOperator();
    const right = this.parseMultiplicative();
    left = new BinaryExpression(left, op, right, left.start, right.end);
  }
  
  return left;
}

private parseMultiplicative(): Expression {
  let left = this.parseExponentiation();
  
  while (this.tokenTable.peekCheck(0, TokenTypes.MULTIPLY) || 
         this.tokenTable.peekCheck(0, TokenTypes.DIVIDE) || 
         this.tokenTable.peekCheck(0, TokenTypes.MODULO)) {
    const op = this.consumeBinaryOperator();
    const right = this.parseExponentiation();
    left = new BinaryExpression(left, op, right, left.start, right.end);
  }
  
  return left;
}

private parseExponentiation(): Expression {
  let left = this.parseUnary();
  
  if (this.tokenTable.peekCheck(0, TokenTypes.EXPONENT)) {
    const op = this.consumeBinaryOperator();
    const right = this.parseExponentiation(); // Right-associative
    return new BinaryExpression(left, op, right, left.start, right.end);
  }
  
  return left;
}

private parseUnary(): Expression {
  if (this.tokenTable.peekCheck(0, TokenTypes.MINUS) || 
      this.tokenTable.peekCheck(0, TokenTypes.NOT) || 
      this.tokenTable.peekCheck(0, TokenTypes.INC) || 
      this.tokenTable.peekCheck(0, TokenTypes.DEC)) {
        
    const token = this.tokenTable.eatCurrentToken(); // Uses eatCurrentToken() for known unary operators
    
    const operand = this.parseUnary();
    
    if (token.type === TokenTypes.MINUS) {
      return new UnaryExpression(
        UnaryOperator.Negate, operand, false,
        token.sourceLocation, operand.end
      );
    } else if (token.type === TokenTypes.NOT) {
      return new UnaryExpression(
        UnaryOperator.Not, operand, false,
        token.sourceLocation, operand.end
      );
    } else if (token.type === TokenTypes.INC) {
      return new UnaryExpression(
        UnaryOperator.IncPrefix, operand, false,
        token.sourceLocation, operand.end
      );
    } else if (token.type === TokenTypes.DEC) {
      return new UnaryExpression(
        UnaryOperator.DecPrefix, operand, false,
        token.sourceLocation, operand.end
      );
    }
  }
  
  return this.parsePrimaryExpression();
}


private parseCallParameters(): CallParameter[] {
  const args: CallParameter[] = [];

  while (!this.tokenTable.peekCheck(0, TokenTypes.RPAREN)) {
    const name = this.parseIdentifier();
    const value = this.parseExpression();

    args.push(new CallParameter(name, value, name.start, value.end));

    if (this.tokenTable.peek().type === TokenTypes.COMMA) {
      this.tokenTable.advance();
    } else {
      break;
    }
  }


  return args;
}

private parseCallExpression(): FunctionCallExpression { 
  const callee = this.parseIdentifier();

  const args = this.parseCallParameters();

  return new FunctionCallExpression(callee, args, callee.start, callee.end);
}

private parsePrimaryExpression(): Expression {
  const token = this.tokenTable.peek();

  // Literal
  if ([TokenTypes.INTEGER, TokenTypes.STRING, TokenTypes.BOOL, TokenTypes.FLOAT].includes(token.type)) {
    this.tokenTable.eatCurrentToken();
    return new Literal(token.value, token.sourceLocation, token.sourceLocation);
  }

  // Function Call or Variable
  if (token.type === TokenTypes.IDENT) {
    // FUNCTION CALL: Use your existing parseCallStatement
    if (this.isCallableStart()) {
      return this.parseCallExpression();
    }

    // VARIABLE: Not a function call
    const name = this.parseIdentifier();

    // POSTFIX: Increment
    if (this.tokenTable.peekCheck(0, TokenTypes.INC)) {
      this.tokenTable.eat(TokenTypes.INC);
      return new UnaryExpression(
        UnaryOperator.IncPostfix,
        name,
        true,
        name.start,
        this.tokenTable.getPreviousSourceLocation()
      );
    }

    // POSTFIX: Decrement
    if (this.tokenTable.peekCheck(0, TokenTypes.DEC)) {
      this.tokenTable.eat(TokenTypes.DEC);
      return new UnaryExpression(
        UnaryOperator.DecPostfix,
        name,
        true,
        name.start,
        this.tokenTable.getPreviousSourceLocation()
      );
    }

    return name;
  }

  // Parentheses
  if (token.type === TokenTypes.LPAREN) {
    this.tokenTable.eat(TokenTypes.LPAREN);
    const expr = this.parseExpression();
    this.tokenTable.eat(TokenTypes.RPAREN);
    return expr;
  }

  throw new Error(`Unexpected token in expression: ${token.type}`);
}
  // !SECTION 


  // ─────────────────────────────────────────────────────────────────────────────
  // SECTION: Parsing statements
  // ─────────────────────────────────────────────────────────────────────────────

  // TODO: If branch parser
  private parseIfBranch(): IfBranch { 
    if (this.tokenTable.peekCheck(0, TokenTypes.IF, TokenTypes.ELIF)) {
      const ifToken = this.tokenTable.eat(TokenTypes.IF, TokenTypes.ELIF);

      const condition = this.parseExpression();
      const block = this.parseBlockStatement();

      return new IfBranch(condition, block, ifToken.sourceLocation, block.end);

    } else if (this.tokenTable.peekCheck(0, TokenTypes.ELSE)) {
      const elseToken = this.tokenTable.eat(TokenTypes.ELSE);

      const block = this.parseBlockStatement();

      return new IfBranch(null, block, elseToken.sourceLocation, block.end);

    } else {
      throw new Error("Expected else");
    }
  }


  // TODO: if parser stub
  private parseIfStatement(): IfStatement {
    const ifBranches: IfBranch[] = [];

    ifBranches.push(this.parseIfBranch());
    
    while(this.tokenTable.peekCheck(0, TokenTypes.ELIF)) {
      ifBranches.push(this.parseIfBranch());
    }

    if (this.tokenTable.peekCheck(0, TokenTypes.ELSE)) {
      ifBranches.push(this.parseIfBranch());
    }
    
    if(ifBranches.length === 0) { 
      throw new Error("Expected if branch");
    }

    // return fully the if ast node
    return new IfStatement( 
      ifBranches,
      ifBranches[0].start,
      ifBranches[ifBranches.length - 1].end
    );
  }
  
  private parseWhileStatement(): WhileStatement { 
    const whileToken = this.tokenTable.eat(TokenTypes.WHILE);

    const condition = this.parseExpression();
    const block = this.parseBlockStatement();

    return new WhileStatement(condition, block, whileToken.sourceLocation, block.end);
  }

  private parseReturnStatement(): ReturnStatement { 
    const returnToken = this.tokenTable.eat(TokenTypes.RETURN);

    const expression = this.parseExpression();

    return new ReturnStatement(expression, returnToken.sourceLocation, returnToken.sourceLocation);
  }    
  // !SECTION 


  // ─────────────────────────────────────────────────────────────────────────────
  // SECTION: Parsing body, expressions
  // ─────────────────────────────────────────────────────────────────────────────
  // TODO: Statement parser
  private parseStatement(): Statement {
    switch (this.tokenTable.peek().type) {
      case TokenTypes.IF:
        return this.parseIfStatement();
      case TokenTypes.WHILE:
        return this.parseWhileStatement();
      case TokenTypes.RETURN:
        return this.parseReturnStatement();
  
      default:
        if (this.isModifier()) {
          const modifiers = this.parseModifiers();
          if (this.isVariableDeclarationStart()) {
            return this.parseVariableDeclaration(modifiers);
          } else {
            throw new Error("Unexpected token after modifier");
          }
        } else if (this.isVariableDeclarationStart()) {
          // Variable declaration with implicit 'mut' modifier
          const modifiers: Modifiers = {
            access: 'internal',
            varFlags: ['mut'],
          } as Modifiers;
          return this.parseVariableDeclaration(modifiers);
        } else {
          // Any other valid expression as a standalone statement
          const expr = this.parseExpression();
          return new ExpressionStatement(expr, expr.start, expr.end);
        }
    }
  }

  // TODO: Stamtements parser
  private parseStatementListUntil(stopToken: TokenTypes): Statement[] {
    const statements: Statement[] = [];
  
    
    while (!this.tokenTable.peekCheck(0, stopToken)) {
      statements.push(this.parseStatement());
    }
  
    return statements;
  }


  // TODO: Block parser
  private parseBlockStatement(): BlockStatement {
    const leftBraceToken = this.tokenTable.eat(TokenTypes.LBRACE);
    const statements = this.parseStatementListUntil(TokenTypes.RBRACE);
    const rightBraceToken = this.tokenTable.eat(TokenTypes.RBRACE);
    return new BlockStatement(
      statements,
      leftBraceToken.sourceLocation,   // start
      rightBraceToken.sourceLocation   // end
    );
  }
  //!SECTION

    

  // ─────────────────────────────────────────────────────────────────────────────
  // SECTION Parsing methods and variables
  // ─────────────────────────────────────────────────────────────────────────────

  // REVIEW: Variable declaration check
  // Checks if current tokens match variable declaration start
  // Example: "x: i32" in "let x: i32;"
  private isVariableDeclarationStart(): boolean {
    return this.tokenTable.peekCheck(0, TokenTypes.IDENT) 
    && this.tokenTable.peekCheck(1, TokenTypes.COLON);
  }
  
  // Parses variable declarations
  // Example: "x: i32 = 5;"
  // REVIEW: Variable declaration parser 
  private parseVariableDeclaration(modifiers: Modifiers): VariableDeclaration {
    const name = this.parseIdentifier();
    this.tokenTable.eat(TokenTypes.COLON);
    const type = this.parseTypeIdentifier();

    let initializer: Expression | null = null;
    
    /*if (this.tokenTable.peekCheck(0, TokenTypes.ASSIGN)) {
      this.tokenTable.eat(TokenTypes.ASSIGN);
      initializer = this.parseExpression();
    } */
      
    return new VariableDeclaration(name, modifiers, type, initializer, name.start, type.end);
  }


  // REVIEW: Callable check
  // Checks if current token is callable start
  private isCallableStart(): boolean {
    return this.tokenTable.peekCheck(0, TokenTypes.IDENT) 
    && this.tokenTable.peekCheck(1, TokenTypes.LPAREN);
  }

  // REVIEW: Callable declaration parser
  // Parses callable declaration (functions/methods)
  // Example: "myFunc(a: i32) -> i32"
  private parseCallableDeclaration(modifiers: Modifiers): CallableDeclaration {
    // name
    const name = this.parseIdentifier();

    // params
    const params: Parameter[] = [];
    this.tokenTable.eat(TokenTypes.LPAREN);
    while (!this.tokenTable.peekCheck(0, TokenTypes.RPAREN)) {
      if(params.length > 0) {
        this.tokenTable.eat(TokenTypes.COMMA)
      }
      const paramModifiers = this.parseModifiers();
      
      const name = this.parseIdentifier();
      this.tokenTable.eat(TokenTypes.COLON)
      const type = this.parseTypeIdentifier();
      

      params.push(new Parameter(name, type, null, name.start, type.end));

      // TODO Add parameter default values
      /*if (this.tokenTable.peekCheck(0, TokenTypes.ASSIGN)) {
      this.tokenTable.eat(TokenTypes.ASSIGN);
      initializer = this.parseExpression();
      } */
    }
    this.tokenTable.eat(TokenTypes.RPAREN);

    if (this.tokenTable.peekCheck(0, TokenTypes.ARROW)) {
      this.tokenTable.eat(TokenTypes.ARROW);
      const returnType = this.parseTypeIdentifier();
      return new CallableDeclaration(name, modifiers, params, returnType, name.start, returnType.end);
    } 

    return new CallableDeclaration(name, modifiers, params, null, name.start, name.end);
  }

  // REVIEW: Callable definition parser
  // Parses callable definitions (functions/methods)
  // Example: "myFunc(a: i32) -> i32 { return a + 1; }"
  private parseCallableDefinition(modifiers: Modifiers): CallableDefinition {
    const declaration = this.parseCallableDeclaration(modifiers) as CallableDefinition;
  
    declaration.body = this.parseBlockStatement();
  
    return declaration;
  }

  //!SECTION





  // ─────────────────────────────────────────────────────────────────────────────
  // SECTION: Parsing type, shard, enum, imp.
  // ─────────────────────────────────────────────────────────────────────────────

  // Helper for parsing definitions in shard and type
  // {<members>}
  // REVIEW
  private parseDeclarations(): (VariableDeclaration | CallableDeclaration)[]{
    const members: (VariableDeclaration | CallableDeclaration)[] = [];

    this.tokenTable.eat(TokenTypes.LBRACE);

    // Keep parsing until we hit RBRACE
    let foundRbrace = false;
    while (!foundRbrace) {
      const memberModifiers = this.parseModifiers();
  
      if (this.isCallableStart()) {
        const method = this.parseCallableDeclaration(memberModifiers);
        members.push(method);
        continue
      } 

      if (this.tokenTable.peekCheck(0, TokenTypes.IDENT)) {
        const variable = this.parseVariableDeclaration(memberModifiers);
        members.push(variable);
        continue
      } 

      if (this.tokenTable.peekCheck(0,TokenTypes.RBRACE)) {
        foundRbrace = true;
        break;
      } 

      throw new Error("Unexpected token: " + this.tokenTable.peek().toString());
    }
    
    this.tokenTable.eat(TokenTypes.RBRACE);

    return members;
  }

  
  // Parses type declarations
  // type MyType { x: i32; new(a: float) -> i32; }
  // REVIEW
  private parseType(modifiers: Modifiers): TypeDeclaration {
    // type
    const typeToken = this.tokenTable.eat(TokenTypes.TYPE);

    // ident
    const name = this.parseIdentifier();

    // {<members>}
    const members: (VariableDeclaration | CallableDeclaration)[] = this.parseDeclarations();

    return new TypeDeclaration(
      name,
      modifiers,
      members,
      typeToken.sourceLocation,
      this.tokenTable.getPreviousSourceLocation()
    );
  }

  // Parses shard declarations
  // shard MyShard { x: i32; }
  // REVIEW
  private parseShard(modifiers: Modifiers): ShardDeclaration {
    // type
    const shardToken = this.tokenTable.eat(TokenTypes.SHARD);

    // ident
    const name = this.parseIdentifier();
    

    // {<members>}
    const members: (VariableDeclaration | CallableDeclaration)[] = this.parseDeclarations();


    return new ShardDeclaration(
      name,
      modifiers,
      members,
      shardToken.sourceLocation,
      this.tokenTable.getPreviousSourceLocation()
    );
  }



  // Parses implementation declarations
  // Example: "impl MyImpl for MyType { method() { ... } }"
  // REVIEW
  private parseImpl(modifiers: Modifiers): ImplDeclaration {
    // impl
    const implToken = this.tokenTable.eat(TokenTypes.IMPL);

    // typeIdent
    const target = this.parseIdentifier();

    let forType: Identifier | null = null
    if (this.tokenTable.peekCheck(0, TokenTypes.FOR)) {
      // for (optional)
      this.tokenTable.eat(TokenTypes.FOR);

      // typeIdent2
      forType = this.parseIdentifier();
    }

    // {method(param:type )}
    const members: CallableDefinition[] = [];

    // Keep parsing until we hit RBRACE
    let foundRbrace = false;
    this.tokenTable.eat(TokenTypes.LBRACE);
    while (!foundRbrace) {
      const memberModifiers = this.parseModifiers();
  
      if (this.isCallableStart()) {
        const method = this.parseCallableDefinition(memberModifiers);
        members.push(method);
        continue
      } 

      if (this.tokenTable.peekCheck(0,TokenTypes.RBRACE)) {
        foundRbrace = true;
        break;
      } 

      throw new Error("Unexpected token: " + this.tokenTable.peek().toString());
    
    }
    this.tokenTable.eat(TokenTypes.RBRACE);


    return new ImplDeclaration(
      target, forType, modifiers, members, 
      implToken.sourceLocation, this.tokenTable.getPreviousSourceLocation()
    );
  }

  // Parses enum declarations
  // enum Color { Red, Green, Blue = 255 }
  // REVIEW
  private parseEnum(modifiers: Modifiers): EnumDeclaration {
    console.log("parsing enum")
    // enum
    const enumToken = this.tokenTable.eat(TokenTypes.ENUM);

    // enumName
    const name = this.parseIdentifier();


    // { Red, Green, Blue = 255 }
    const variants: EnumVariant[] = [];
    
    let foundRbrace = false;
    this.tokenTable.eat(TokenTypes.LBRACE);
    while (!foundRbrace) {    


      if (this.tokenTable.peekCheck(0, TokenTypes.RBRACE)) {
        foundRbrace = true;
        break;

      } 
      if (this.tokenTable.peekCheck(0, TokenTypes.IDENT)) {
        let value: Expression | null = null;
        const variantName = this.parseIdentifier();
        
        if (this.tokenTable.peekCheck(0, TokenTypes.EQ)) {
          this.tokenTable.advance();
          value = this.parseExpression();
        }

        variants.push(new EnumVariant(variantName, value));

        this.tokenTable.eat(TokenTypes.SEMICOLON);
        continue
      }  

      throw new Error("Unexpected token in enumeraor: " + this.tokenTable.peek().toString());
    }
    this.tokenTable.eat(TokenTypes.RBRACE);
    
    return new EnumDeclaration(
      name, modifiers, variants, 
      enumToken.sourceLocation, this.tokenTable.getPreviousSourceLocation()
    );
  }
  // !SECTION



  // ─────────────────────────────────────────────────────────────────────────────
  // SECTION Main parsing logic
  // ─────────────────────────────────────────────────────────────────────────────

  // Main program parser
  // REVIEW
  private parseProgram(): Program {

    const body: Declaration[] = [];
    
    // Parse top-level declarations until EOF
    while (!this.tokenTable.peekCheck(0, TokenTypes.EOF)) {

      const modifiers = this.parseModifiers();

      let declaration: Declaration | null = null;
      
      // Determine declaration type
      switch(this.tokenTable.peek().type) {
        case(TokenTypes.TYPE):
          declaration = this.parseType(modifiers);
          break;
        case(TokenTypes.SHARD):
          declaration = this.parseShard(modifiers);
          break;
        case(TokenTypes.IMPL):
          declaration = this.parseImpl(modifiers);
          break;
        case(TokenTypes.ENUM):
          declaration = this.parseEnum(modifiers);
          break;
      }
      
      if (!declaration && this.isCallableStart()) {
        declaration = this.parseCallableDefinition(modifiers);

      }  
      if (!declaration && this.tokenTable.peekCheck(0, TokenTypes.IDENT)) {
        declaration = this.parseVariableDeclaration(modifiers);
      }


      if (declaration) {
        body.push(declaration);
      } else {
        throw new Error(`Unexpected token in program: ${this.tokenTable.peek().toString()}`);
      }
    }
    
    // Create program node with source locations
    const startLoc = body.length > 0 
      ? body[0].start 
      : { line: 0, column: 0, offset: 0, file: "" };
    const endLoc = this.tokenTable.getPreviousSourceLocation();
    return new Program(body, startLoc, endLoc);
  }

  // Main parser entry point
  visit(self: TokenTable): void {
    this.tokenTable = self;
    this.program = this.parseProgram(); // Parse entire program AST
  }
  // !SECTION
}