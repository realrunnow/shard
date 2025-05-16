import { TokenTable, TokenTableVisitor } from "../tokens/token_table";

export class Parser implements TokenTableVisitor{
    visit(self: TokenTable): void {
        console.log("visiting")
    }
}