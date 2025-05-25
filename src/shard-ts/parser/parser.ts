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
  FunctionCallExpression,
  MemberExpression
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

  // Define operator precedence and associativity
  private operatorPrecedence: Map<TokenTypes, { precedence: number, rightAssociative: boolean }> = new Map([
    // Assignment (lowest precedence)
    [TokenTypes.ASSIGN, { precedence: 1, rightAssociative: true }],
    [TokenTypes.PLUS_ASSIGN, { precedence: 1, rightAssociative: true }],
    [TokenTypes.MINUS_ASSIGN, { precedence: 1, rightAssociative: true }],
    [TokenTypes.MULTIPLY_ASSIGN, { precedence: 1, rightAssociative: true }],
    [TokenTypes.DIVIDE_ASSIGN, { precedence: 1, rightAssociative: true }],
    
    // Conditional
    [TokenTypes.QUESTION_MARK, { precedence: 2, rightAssociative: true }],
    
    // Logical OR
    [TokenTypes.OR, { precedence: 3, rightAssociative: false }],
    
    // Logical AND
    [TokenTypes.AND, { precedence: 4, rightAssociative: false }],
    
    // Equality
    [TokenTypes.EQ, { precedence: 5, rightAssociative: false }],
    [TokenTypes.NE, { precedence: 5, rightAssociative: false }],
    
    // Relational
    [TokenTypes.LT, { precedence: 6, rightAssociative: false }],
    [TokenTypes.GT, { precedence: 6, rightAssociative: false }],
    [TokenTypes.LE, { precedence: 6, rightAssociative: false }],
    [TokenTypes.GE, { precedence: 6, rightAssociative: false }],
    
    // Additive
    [TokenTypes.PLUS, { precedence: 7, rightAssociative: false }],
    [TokenTypes.MINUS, { precedence: 7, rightAssociative: false }],
    
    // Multiplicative
    [TokenTypes.MULTIPLY, { precedence: 8, rightAssociative: false }],
    [TokenTypes.DIVIDE, { precedence: 8, rightAssociative: false }],
    [TokenTypes.MODULO, { precedence: 8, rightAssociative: false }],
    
    // Exponentiation (highest precedence)
    [TokenTypes.EXPONENT, { precedence: 9, rightAssociative: true }],
  ]);

  // Map token types to binary operators
  private tokenToBinaryOperator: Map<TokenTypes, BinaryOperator> = new Map([
    [TokenTypes.PLUS, BinaryOperator.Add],
    [TokenTypes.MINUS, BinaryOperator.Subtract],
    [TokenTypes.MULTIPLY, BinaryOperator.Multiply],
    [TokenTypes.DIVIDE, BinaryOperator.Divide],
    [TokenTypes.MODULO, BinaryOperator.Modulo],
    [TokenTypes.EXPONENT, BinaryOperator.Power],
    [TokenTypes.EQ, BinaryOperator.Equals],
    [TokenTypes.NE, BinaryOperator.NotEquals],
    [TokenTypes.LT, BinaryOperator.LessThan],
    [TokenTypes.GT, BinaryOperator.GreaterThan],
    [TokenTypes.LE, BinaryOperator.LessThanOrEqual],
    [TokenTypes.GE, BinaryOperator.GreaterThanOrEqual],
    [TokenTypes.AND, BinaryOperator.And],
    [TokenTypes.OR, BinaryOperator.Or],
    [TokenTypes.ASSIGN, BinaryOperator.Assign],
    [TokenTypes.PLUS_ASSIGN, BinaryOperator.AddAssign],
    [TokenTypes.MINUS_ASSIGN, BinaryOperator.SubtractAssign],
    [TokenTypes.MULTIPLY_ASSIGN, BinaryOperator.MultiplyAssign],
    [TokenTypes.DIVIDE_ASSIGN, BinaryOperator.DivideAssign],
  ]);

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



private parseExpression(): Expression {
  return this.parseExpressionWithPrecedence();
}

private parseExpressionWithPrecedence(minPrecedence: number = 0): Expression {
  let left = this.parseUnaryExpression();
  
  // Handle conditional expression (ternary) as a special case
  if (this.tokenTable.peekCheck(0, TokenTypes.QUESTION_MARK)) {
    this.tokenTable.eat(TokenTypes.QUESTION_MARK);
    const thenBranch = this.parseExpression();
    this.tokenTable.eat(TokenTypes.COLON);
    const elseBranch = this.parseExpressionWithPrecedence(0);
    return new ConditionalExpression(
      left, thenBranch, elseBranch, 
      left.start, elseBranch.end
    );
  }
  
  // Process binary operators according to precedence
  while (true) {
    const token = this.tokenTable.peek();
    const opInfo = this.operatorPrecedence.get(token.type);
    
    // If no operator or precedence is lower than minimum, stop
    if (!opInfo || opInfo.precedence < minPrecedence) {
      break;
    }
    
    // Consume the operator token
    this.tokenTable.advance();
    
    // For right-associative operators, use current precedence - 1
    // For left-associative operators, use current precedence + 1
    const nextMinPrecedence = opInfo.rightAssociative ? 
      opInfo.precedence : 
      opInfo.precedence + 1;
    
    // Parse the right side with the appropriate precedence
    const right = this.parseExpressionWithPrecedence(nextMinPrecedence);
    
    // Create binary expression
    const operator = this.tokenToBinaryOperator.get(token.type);
    if (!operator) {
      throw new Error(`Unknown binary operator: ${token}`);
    }
    
    left = new BinaryExpression(left, operator, right, left.start, right.end);
  }
  
  return left;
}

private parseUnaryExpression(): Expression {
  if (this.tokenTable.peekCheck(0, TokenTypes.MINUS, TokenTypes.NOT, TokenTypes.INC, TokenTypes.DEC)) {
    const token = this.tokenTable.eatCurrentToken();
    const operand = this.parseUnaryExpression();
    
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

private parsePrimaryExpression(): Expression {
  const token = this.tokenTable.peek();

  // Literal
  if (this.tokenTable.peekCheck(0, TokenTypes.INTEGER, TokenTypes.STRING, TokenTypes.BOOL, TokenTypes.FLOAT)) {
    this.tokenTable.eatCurrentToken();
    return new Literal(token.value, token.sourceLocation, token.sourceLocation);
  }

  // Function Call, Member Access, or Variable
  if (this.tokenTable.peekCheck(0, TokenTypes.IDENT)) {
    // Parse identifier first
    const name = this.parseIdentifier();
    
    // Check if it's a function call
    if (this.tokenTable.peekCheck(0, TokenTypes.LPAREN)) {
      this.tokenTable.eat(TokenTypes.LPAREN);
      const args = this.parseCallParameters();
      this.tokenTable.eat(TokenTypes.RPAREN);
      return new FunctionCallExpression(name, args, name.start, this.tokenTable.getPreviousSourceLocation());
    }
    
    // Check if it's a member access
    if (this.tokenTable.peekCheck(0, TokenTypes.DOT)) {
      return this.parseMemberExpression(name);
    }

    // Check for postfix operators
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

    // Just a variable reference
    return name;
  }

  // Parentheses
  if (this.tokenTable.peekCheck(0, TokenTypes.LPAREN)) {
    this.tokenTable.eat(TokenTypes.LPAREN);
    const expr = this.parseExpression();
    this.tokenTable.eat(TokenTypes.RPAREN);
    return expr;
  }
  


  throw new Error(`Unexpected token in expression: ${token}`);
}

private parseCallParameters(): CallParameter[] {
  const args: CallParameter[] = [];

  while (!this.tokenTable.peekCheck(0, TokenTypes.RPAREN)) {
    let name;

    if (this.tokenTable.peekCheck(0, TokenTypes.IDENT)) {
      name = this.parseIdentifier()
      this.tokenTable.eat(TokenTypes.ASSIGN)
    } else {
      name = null
    }

    const value = this.parseExpression();

    args.push(new CallParameter(name, value, name ? name.start : value.start, value.end));

    if (this.tokenTable.peekCheck(0, TokenTypes.COMMA)) {
      this.tokenTable.advance();
    } else {
      break;
    }
  }

  return args;
}

private parseMemberExpression(object: Expression): Expression {
  this.tokenTable.eat(TokenTypes.DOT);
  const property = this.parseIdentifier();
  const memberExpr = new MemberExpression(object, property, object.start, property.end);
  
  // Check for further member access (a.b.c)
  if (this.tokenTable.peekCheck(0, TokenTypes.DOT)) {
    return this.parseMemberExpression(memberExpr);
  }
  
  // Check for function call on member (a.b())
  if (this.tokenTable.peekCheck(0, TokenTypes.LPAREN)) {
    this.tokenTable.eat(TokenTypes.LPAREN);
    const args = this.parseCallParameters();
    this.tokenTable.eat(TokenTypes.RPAREN);
    return new FunctionCallExpression(memberExpr as any, args, object.start, this.tokenTable.getPreviousSourceLocation());
  }
  
  return memberExpr;
}
  // !SECTION 


  // ─────────────────────────────────────────────────────────────────────────────
  // SECTION: Parsing statements
  // ─────────────────────────────────────────────────────────────────────────────

  // TODO: If branch parser
  private parseIfBranch(): IfBranch { 
    if (this.tokenTable.peekCheck(0, TokenTypes.IF, TokenTypes.ELIF)) {
      const ifToken = this.tokenTable.eat(TokenTypes.IF, TokenTypes.ELIF);

      this.tokenTable.eat(TokenTypes.LPAREN);
      const condition = this.parseExpression();
      this.tokenTable.eat(TokenTypes.RPAREN)

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

    this.tokenTable.eat(TokenTypes.LPAREN)
    const condition = this.parseExpression();
    this.tokenTable.eat(TokenTypes.RPAREN)

    const block = this.parseBlockStatement();

    return new WhileStatement(condition, block, whileToken.sourceLocation, block.end);
  }

  private parseReturnStatement(): ReturnStatement { 
    const returnToken = this.tokenTable.eat(TokenTypes.RETURN);

    const expression = this.parseExpression();
    
    this.tokenTable.eat(TokenTypes.SEMICOLON);


    return new ReturnStatement(expression, returnToken.sourceLocation, expression.end);
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
        const returnStmt = this.parseReturnStatement();
        return returnStmt;
  
        default:
          if (this.isModifier()) {
            const modifiers = this.parseModifiers();
            if (this.isVariableDeclarationStart()) {
              const varDecl = this.parseVariableDeclaration(modifiers);

              return varDecl;
            } else {
              throw new Error("Unexpected token after modifier");
            }
          } else if (this.isVariableDeclarationStart()) {
            // Variable declaration with implicit 'mut' modifier
            const modifiers: Modifiers = {
              access: 'internal',
              varFlags: ['mut'],
            } as Modifiers;
            const varDecl = this.parseVariableDeclaration(modifiers);

            return varDecl;
          } else {
            // Any other valid expression as a standalone statement
            const expr = this.parseExpression();
            this.tokenTable.eat(TokenTypes.SEMICOLON);
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
    
    if (this.tokenTable.peekCheck(0, TokenTypes.ASSIGN)) {
      this.tokenTable.eat(TokenTypes.ASSIGN);
      initializer = this.parseExpression();
    } 
      
    this.tokenTable.eat(TokenTypes.SEMICOLON);

    return new VariableDeclaration(name, modifiers, type, initializer, name.start, type.end);
  }


  // REVIEW: Callable check
  // Checks if current token is callable start
  private isCallableStart(): boolean {
    // Check if we have an identifier followed by a left parenthesis
    return this.tokenTable.peekCheck(0, TokenTypes.IDENT) && 
           this.tokenTable.peekCheck(1, TokenTypes.LPAREN);
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

    // Consume semicolon after callable declaration
    if (this.tokenTable.peekCheck(0, TokenTypes.SEMICOLON)) {
      this.tokenTable.eat(TokenTypes.SEMICOLON);
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
  private parseDeclarations(): (VariableDeclaration | CallableDeclaration)[]{    const members: (VariableDeclaration | CallableDeclaration)[] = [];

    this.tokenTable.eat(TokenTypes.LBRACE);

    // Keep parsing until we hit RBRACE
    let foundRbrace = false;
    while (!foundRbrace) {
      const memberModifiers = this.parseModifiers();
  
      if (this.isCallableStart()) {
        const method = this.parseCallableDeclaration(memberModifiers);
        members.push(method);
        

        
        continue;
      } 

      if (this.tokenTable.peekCheck(0, TokenTypes.IDENT)) {
        const variable = this.parseVariableDeclaration(memberModifiers);
        members.push(variable);
        
        
        continue;
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
          const token = this.tokenTable.peek();
          throw new Error(`Unexpected token in program: ${token.toString()}`);
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
    try {
      this.program = this.parseProgram(); // Parse entire program AST
    } catch (error) {
      console.error('Parser error:', error);
      // Re-throw with more context if needed
      throw error;
    }
  }
  // !SECTION
}