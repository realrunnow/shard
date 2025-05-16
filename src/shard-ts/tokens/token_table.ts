
import { SourceLocation } from "../shared/meta";
import { Token } from "./token"
import { TokenTypes } from "./token_types";


export interface TokenTableVisitor {
    visit(self:TokenTable) : void
}


export class TokenTable {
    private position = 0;

    private tokens: Token[] = [];
    private text!: string;


    public getLine(): number {
        return this.peek().sourceLocation.line
    }

    public getColumn(): number {
        return this.peek().sourceLocation.column
    }

    public getPosition(): number {
        return this.position;
    }


    // --- Input Navigation Methods ---
    public advance(ahead:number = 1): void {
        this.position += ahead
    }

    public peek(ahead:number = 0): Token {
        const position = this.getPosition() + ahead;

        return this.tokens[position]
    }

    public peekCheck(ahead:number = 0, ...tokenTypes: TokenTypes[]): boolean {
        return tokenTypes.includes(
            this.peek(ahead).type
        )
    }

    public eat(...tokenTypes: TokenTypes[]): Token {
        if (!tokenTypes.includes(TokenTypes.EOL)){
            while (this.peek().type == TokenTypes.EOL) {
                this.advance(); // Skip EOL unless it's one of the expected types
            }
        }
    
        const currentToken = this.peek();
        const currentType = currentToken.type;
    
        if (tokenTypes.includes(currentType)) {
            this.advance();
            return currentToken
        } else {
            throw new Error(
                `Expected one of [${tokenTypes.map(type => TokenTypes[type]).join(", ")}], got ${TokenTypes[currentType]} at line ${this.getLine()}, column ${this.getColumn()}`
              );
        }
    }

    public rewind(): void {
        this.position = 0
    }


    // --- Token Management ---
    public push(token: Token): void {
        this.tokens.push(token);
    }

    public getTokens(): Token[] {
        return this.tokens;
    }
    public getText(): string {
        return this.text;
    }
    public setText(text:string) {
        this.text = text
    }


    // --- New Method: Get Previous Token's Source Location ---
    public getPreviousSourceLocation(): SourceLocation {
        if (this.position === 0) {
        throw new Error("No previous token available");
        }
        return this.tokens[this.position - 1].sourceLocation;
    }
    
    public eatCurrentToken(): Token {
        if (this.position >= this.tokens.length) {
          // Handle unexpected EOF gracefully with location context
          const lastToken = this.tokens[this.tokens.length - 1];
          const location = lastToken 
            ? ` at line ${lastToken.sourceLocation.line}, column ${lastToken.sourceLocation.column}` 
            : '';
          
          throw new Error(`Unexpected end of input${location}`);
        }
      
        const token = this.tokens[this.position];
        this.position++;
        return token;
      }

    // --- Visitor Pattern Hook ---
    public accept(visitor: TokenTableVisitor): void {
        visitor.visit(this);
    }

}