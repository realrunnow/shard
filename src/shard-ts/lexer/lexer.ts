import { SourceLocation } from "../shared/meta";
import { TokenTableVisitor, TokenTable } from "../tokens/token_table"
import { TokenTypes } from "../tokens/token_types";
import { Token } from "../tokens/token";

import {
    PATTERNS
} from "./patterns"

const PATTERNS_KEYS = Object.keys(PATTERNS).sort((a, b) => b.length - a.length)

/**
 * A lexer that tokenizes input text according to predefined rules.
 * Implements the TokenTableVisitor interface to configure itself using a TokenTable.
 */
export class Lexer implements TokenTableVisitor {

    private text: string
    constructor(text:string) {
        this.text = text
    }

    ///// tokentable helper
    private tokenTable!: TokenTable
    private getText(): string {
        return this.tokenTable.getText();
    }
    private addToken(tokenType: TokenTypes, value: any): void {
        const start = new SourceLocation(
            this.sourceLocation.line, 
            this.sourceLocation.column, 
            this.sourceLocation.file
        )

        const token = new Token(tokenType, value, start);
        this.tokenTable.push(token);
    }


    ///// leocation meta
    private sourceLocation: SourceLocation = new SourceLocation();
    private nextLine(): void {
        this.setColumn(1);
        this.sourceLocation.line++;
    }

    private nextColumn(by: number = 1): void {
        this.sourceLocation.column += by;
        this.nextChar(by);
    }

    private setColumn(column: number): void {
        this.sourceLocation.column = column;
    }
    
    
    ///// lexer pos
    private lexerPosition: number = 0;
    private getChar(): string {
        return this.getText()[this.lexerPosition];
    }

    private nextChar(by: number = 1): void {
        this.lexerPosition += by;
    }


    ///// utility
    private getRemainingText(): string {
        return this.tokenTable.getText().substring(this.lexerPosition);
    }

    private isWhitespace(): boolean {
        return /\s/.test(this.getChar());
    }
    
    private isDigit(): boolean {
        const ch = this.getChar();
        return ch >= '0' && ch <= '9';
    }

    private isEOL(): boolean {
        return this.getChar() == "\n" || this.getChar() == ";";
    }

    private isEOF(): boolean {
        return this.lexerPosition >= this.getText().length;
    }

    private parseWrappedToken(start: string, end: string, tokenType: TokenTypes, allowEOL: boolean = true): boolean {
        const remainder = this.getRemainingText();
    
        if (!remainder.startsWith(start)) {
            return false;
        }
    
        this.nextColumn(start.length);
        let accumulatedString = "";
    
        while (!this.isEOF()) {
            const currentRemainder = this.getRemainingText();
    
            if (currentRemainder.startsWith(end)) {
                this.addToken(tokenType, accumulatedString);
                if(end == "\n") {
                    this.nextColumn(end.length);
                    this.addToken(TokenTypes.EOL, "");
                    this.nextLine()
                } else {
                    this.nextColumn(end.length);
                }
                return true;
            }
    
            if (this.isEOL() && !allowEOL) {
                break; // end not found before EOL in single-line context
            }
    
            accumulatedString += this.getChar();
            this.nextColumn();
        }
    
        if (this.isEOF() && !remainder.startsWith(end)) {
            throw new Error(`Unterminated ${TokenTypes[tokenType]} starting with '${start}'`);
        }
    
        return false;
    }
    
    ///// tokenizer methods
    private tokenizeWhitespaceAndNewlines(): boolean {
        const char: string = this.getChar();

        if (this.isWhitespace()) {
            if (this.isEOL()) {
                this.addToken(TokenTypes.EOL, "")

                this.nextLine();

                this.nextColumn();
                return true;
            } 
        } 

        return false;
    }

    private tokenizeComments(): boolean {
        return this.parseWrappedToken("//", "\n", TokenTypes.COMMENT, false)
            || this.parseWrappedToken("/*", "*/", TokenTypes.COMMENT, true);
    }

    private tokenizeString(): boolean {
        return this.parseWrappedToken('"', '"', TokenTypes.STRING, true)
    }

    private tokenizeFloat(): boolean {
        const remainder = this.getRemainingText();
        const floatMatch = remainder.match(/^[0-9]+\.[0-9]+/);
        if (!floatMatch) {
            return false;
        }
        const matchStr = floatMatch[0];
        this.nextColumn(matchStr.length);
        this.addToken(TokenTypes.FLOAT, matchStr);
        return true;
    }

    private tokenizeInteger(): boolean {
        const remainder = this.getRemainingText();
        const intMatch = remainder.match(/^[0-9]+/);
        if (!intMatch) {
            return false;
        }
        const matchStr = intMatch[0];
        this.nextColumn(matchStr.length);
        this.addToken(TokenTypes.INTEGER, matchStr);
        return true;
    }

    private tokenizeOperators(): boolean{
        const remainder: string = this.getRemainingText();
        let foundToken: TokenTypes = TokenTypes.UNKNOWN
        let foundLength: number = 0;
        let foundValue = "";

        for (const pattern of PATTERNS_KEYS) {
            if (remainder.startsWith(pattern)) {
                foundToken = PATTERNS[pattern]
                foundLength = pattern.length
                foundValue = remainder.substring(0, foundLength)
                break
            }
        }  
         

        if (foundToken != TokenTypes.UNKNOWN) {
            this.addToken(foundToken, foundValue)

            this.nextColumn(foundLength)
            return true;
        }

        return false;
    }

    private tokenizeIdentifier(): boolean {
        const remainder = this.getRemainingText();
    
        // Identifiers must start with a letter or underscore
        const idStart = remainder.charAt(0);
        if (!/[A-Za-z_]/.test(idStart)) {
            return false;
        }
    
        let accumulatedString = idStart;
        this.nextColumn();
    
        // Continue while letters, digits, or underscores
        while (!this.isEOF()) {
            const ch = this.getChar();
            if (!/[A-Za-z0-9_]/.test(ch)) {
                break;
            }
            accumulatedString += ch;
            this.nextColumn();
        }
    
        this.addToken(TokenTypes.IDENT, accumulatedString);
        return true;
    }
    

    private tokenizeNext() {
        if (this.tokenizeWhitespaceAndNewlines()) return;
        if (this.tokenizeComments()) return;
        if (this.tokenizeString()) return;
        if (this.tokenizeOperators()) return;
        if (this.tokenizeIdentifier()) return;
        if (this.tokenizeFloat()) return;
        if (this.tokenizeInteger()) return;

        this.nextColumn();
    }

    public tokenize(): void {
        while (!this.isEOF()) {
            this.tokenizeNext();
        }

        this.addToken(TokenTypes.EOF, "")
    }

    public visit(table: TokenTable): void {
        this.tokenTable = table
        this.tokenTable.setText(this.text)
        this.tokenize();
    }
}
