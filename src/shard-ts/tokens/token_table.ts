
import { Token } from "./token"
import { TokenTypes } from "./token_types";


export interface TokenTableVisitor {
    visit(self:TokenTable) : void
}


export class TokenTable {
    private position = 0;

    private tokens: Token[] = [];
    constructor(private text: string) {}


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

    public eat(...tokenTypes: TokenTypes[]): void {
        const currentType = this.peek().type;
    
        if (tokenTypes.includes(currentType)) {
            this.advance();
        } else {
            throw new Error(`Expected one of [${tokenTypes.join(", ")}], got ${currentType} at line ${this.getLine()}, column ${this.getColumn()}`);
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

    // --- Visitor Pattern Hook ---
    public accept(visitor: TokenTableVisitor): void {
        visitor.visit(this);
    }
}