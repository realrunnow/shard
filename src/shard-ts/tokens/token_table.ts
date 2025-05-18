import { SourceLocation } from "../shared/meta";
import { Token } from "./token";
import { TokenTypes } from "./token_types";

export interface TokenTableVisitor {
    visit(self: TokenTable): void;
}

const SKIPPABLE_TOKENS = new Set<TokenTypes>([
    TokenTypes.EOL,
    TokenTypes.COMMENT
]);

export class TokenTable {
    private position = 0;
    private tokens: Token[] = [];
    private text!: string;

    public getLine(): number {
        return this.peek().sourceLocation.line;
    }

    public getColumn(): number {
        return this.peek().sourceLocation.column;
    }

    public getPosition(): number {
        return this.position;
    }

    // --- Input Navigation Methods ---
    public advance(ahead: number = 1): void {
        this.position += ahead;
    }

    private lookAhead(offset: number = 0, skipSkippables: boolean = true): Token {
        let pos = this.position + offset;
    
        while (pos < this.tokens.length) {
            const token = this.tokens[pos];
            if (!skipSkippables || !SKIPPABLE_TOKENS.has(token.type)) {
                return token;
            }
            pos++;
        }
    
        // At this point, we've gone past the end of the token list
    
        if (this.tokens.length === 0) {
            throw new Error("Unexpected end of input: No tokens available");
        }
    
        // If the last token is EOF or non-skippable, return it
        const lastToken = this.tokens[this.tokens.length - 1];
        if (!SKIPPABLE_TOKENS.has(lastToken.type)) {
            return lastToken;
        }
    
        // If all remaining tokens were skippable, and no non-skippable tokens exist
        throw new Error("Unexpected end of input: No non-skippable tokens found after skipping");
    }

    public peek(ahead: number = 0): Token {
        return this.lookAhead(ahead);
    }

    public peekCheck(ahead: number = 0, ...tokenTypes: TokenTypes[]): boolean {
        const token = this.lookAhead(ahead);
        return tokenTypes.includes(token.type);
    }

    public eat(...tokenTypes: TokenTypes[]): Token {
        const skipSkippables = !tokenTypes.some(t => SKIPPABLE_TOKENS.has(t));
        let i = this.position;
        let foundIndex = -1;
        let foundToken: Token | null = null;
    
        while (i < this.tokens.length) {
            const token = this.tokens[i];
            if (skipSkippables && SKIPPABLE_TOKENS.has(token.type)) {
                i++;
                continue;
            }
    
            if (tokenTypes.includes(token.type)) {
                foundIndex = i;
                foundToken = token;
                break;
            } else {
                // If not skipping, stop immediately
                if (!skipSkippables) {
                    break;
                }
                i++;
            }
        }
    
        if (foundToken === null) {
            const lastToken = this.tokens[this.tokens.length - 1];
            const location = lastToken
                ? ` at line ${lastToken.sourceLocation.line}, column ${lastToken.sourceLocation.column}`
                : "";
            throw new Error(
                `Expected one of [${tokenTypes.map(type => TokenTypes[type]).join(", ")}], got EOF${location}`
            );
        }
    
        this.position = foundIndex + 1; // Move past the consumed token
        return foundToken;
    }

    public rewind(): void {
        this.position = 0;
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

    public setText(text: string) {
        this.text = text;
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
                : "";

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