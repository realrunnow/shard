import { SourceLocation } from "../shared/meta";
import { TokenTypes } from "./token_types";

export class Token {
    constructor(
        public type: TokenTypes,
        public value: any,
        public sourceLocation: SourceLocation
    ) {}

    toString(): string {
        const limit = 20
        const typeStr = TokenTypes[this.type];
        const valueStr = this.value.length > limit 
            ? this.value.substring(0, limit - 3) + "..." 
            : this.value;
    
        const pad = (str: string, len: number) => str.padEnd(len, ' ');
    
        return [
    
    
            "| " + pad(typeStr, 10) + 
            "| " + pad(valueStr, limit) + 
            "| " + pad(this.sourceLocation.line.toString(), 6) + 
            "| " + pad(this.sourceLocation.column.toString(), 8) + 
            "| " + this.sourceLocation.file
        ].join("\n");
    
    }
}