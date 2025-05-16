export class SourceLocation {
    constructor(
        public line: number = 1,
        public column: number = 1,
        public file: string = ""
    ) {}
}