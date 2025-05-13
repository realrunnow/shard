def encode_token(token):
    """Format a token for display"""
    return f"{token.type.name}({repr(token.value)}) at line {token.line}, col {token.column}"
 
def encode_tokens(tokens):
    """Encode a list of tokens in a readable format"""
    return "\n".join(encode_token(token) for token in tokens) 