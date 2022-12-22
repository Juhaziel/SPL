# Class representing a Solar IR token.
# Exposes token types.
class Token:
    T_KEYWORD = "KEYWORD"
    T_NAME = "NAME"
    T_TYPE = "TYPE"
    T_INT = "INT"
    T_CHAR = "INT" # CHAR is basically the same as INT
    T_STR = "STR"
    T_ALIGN = "ALIGN"
    T_OP = "OP"
    T_RELOP = "RELOP"
    T_LPAR = "LPAR" # (
    T_RPAR = "RPAR" # )
    T_LBRACE = "LBRC" # { 
    T_RBRACE = "RBRC" # }
    T_LBRACKET = "LBRA" # [
    T_RBRACKET = "RBRA" # ]
    T_SEMICOLON = "SEMICOLON" # ;
    T_COLON = "COLON" # :
    T_COMMA = "COMMA" # ,
    T_ASSIGN = "ASSIGN" # =
    T_SIGNED = "T_SIGN" # $
    T_EOF = "EOF"
    
    def __init__(self, type, value, linenum=-1, linepos=-1, **kwargs):
        self.type = type
        self.value = value
        self.extra = kwargs
        self.linenum = linenum
        self.linepos = linepos
    
    def __str__(self):
        value = self.value
        if self.type == Token.T_STR:
            value = bytes(value).decode('utf8')
        if self.type == Token.T_CHAR and self.extra.get("wasChar"):
            value = chr(value)
        if len(self.extra) > 0:
            return f"Token({self.type}, {repr(value)}, {self.extra})"
        return f"Token({self.type}, {repr(value)})"
    
    def __repr__(self):
        return self.__str__()

# Class representing an active Lexer.
# Expects source code to be passed to its constructor
class Lexer:
    PUNCTUATOR_CHARS = "(){}[];:,=!<>+-*/%&!^~!#?$"
    BASE_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    KEYWORDS = [
        ("align1", Token.T_ALIGN),  ("align2", Token.T_ALIGN), ("align4", Token.T_ALIGN),   ("align8", Token.T_ALIGN),   ("alignp", Token.T_ALIGN),
        ("const", Token.T_KEYWORD), ("data", Token.T_KEYWORD), ("else", Token.T_KEYWORD),   ("export", Token.T_KEYWORD), ("foreign", Token.T_KEYWORD),
        ("goto", Token.T_KEYWORD),  ("if", Token.T_KEYWORD),   ("import", Token.T_KEYWORD), ("jump", Token.T_KEYWORD),
        ("pass", Token.T_KEYWORD),  ("ptr", Token.T_TYPE),     ("return", Token.T_KEYWORD), ("weak", Token.T_KEYWORD), 
        ("word1", Token.T_TYPE),    ("word2", Token.T_TYPE),   ("word4", Token.T_TYPE),     ("word8", Token.T_TYPE)
    ]
    PUNCTUATORS = [
        ("+", Token.T_OP), ("-", Token.T_OP), ("*", Token.T_OP), ("/", Token.T_OP), ("/$", Token.T_OP), ("%", Token.T_OP), ("%$", Token.T_OP), # Add, Sub, Mul, Div, Signed Div, Mod, Signed Mod
        ("&", Token.T_OP), ("|", Token.T_OP), ("^", Token.T_OP), ("~&", Token.T_OP), ("~|", Token.T_OP), ("~^", Token.T_OP), # AND, OR, XOR, NAND' NOR, XNOR
        ("<<", Token.T_OP), (">>", Token.T_OP), (">>$", Token.T_OP), # Left Shift, Right Shift Logical, Right Shift Arith
        
        ("==", Token.T_RELOP), ("!=", Token.T_RELOP), # Equal, Not Equal
        (">", Token.T_RELOP), ("<", Token.T_RELOP), (">=", Token.T_RELOP), ("<=", Token.T_RELOP), # Bigger, Smaller, Bigger or Equal, Smaller or Equal (Unsigned)
        (">$", Token.T_RELOP), ("<$", Token.T_RELOP), (">=$", Token.T_RELOP), ("<=$", Token.T_RELOP), # Bigger, Smaller, Bigger or Equal, Smaller or Equal (Signed)
        
        ("(", Token.T_LPAR), (")", Token.T_RPAR),
        ("{", Token.T_LBRACE), ("}", Token.T_RBRACE), 
        ("[", Token.T_LBRACKET), ("]", Token.T_RBRACKET),
        (";", Token.T_SEMICOLON), (":", Token.T_COLON), (",", Token.T_COMMA),
        ("=", Token.T_ASSIGN),
        ("$", Token.T_SIGNED)
    ]
    TYPE_SIZE_SUFFIX = {
        "default": "word1",
        "d": "word2",
        "q": "word4",
        "o": "word8"
    }
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.linenum = 1
        self.linepos = 1

    def __error(self, text):
        raise Exception(f"[LEXER]: An error occured while reading tokens.\n{text}")
    
    # Advance the current character by one and update current_chair, pos
    def __advance(self, num=1):
        self.pos += num
        self.linepos += num
        if self.pos >= len(self.text):
            self.current_char = None # End of File
        else:
            self.current_char = self.text[self.pos]
    
    # Peek ahead a certain number of characters  
    def __peek(self, numchars):
        return self.text[self.pos:self.pos+numchars]
    
    # Skip consecutive whitespace characters
    def __skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            if self.current_char == "\n":
                self.linenum += 1
                self.linepos = 0
            self.__advance()
    
    # Extract a Name or Keyword from text
    def __read_name(self):
        name = ""
        if not self.current_char:
            self.__error(f"{self.linenum},{self.linepos}: Expected name, got EOF")
        
        if not ((self.current_char.isalpha() and self.current_char.isascii()) or self.current_char in "_.@"):
            self.__error(f"{self.linenum},{self.linepos}: Invalid name starting character '{self.current_char}'")
        
        start = (self.linenum, self.linepos)
        
        while self.current_char.isalnum() or self.current_char in "_.@":
            name += self.current_char
            self.__advance()
            if not self.current_char:
                break
        
        # Check for keyword
        equals_keyword = None
        
        for keyword in Lexer.KEYWORDS:
            if keyword[0] == name:
                equals_keyword = keyword[1]
        
        # Strip initial @ if any
        if not equals_keyword and name.startswith("@"):
            name = name[1:]
            
        return Token(equals_keyword if equals_keyword else Token.T_NAME, name, start[0], start[1])
        
    # Extract an integer in a specified base
    def __read_integer(self, base):
        if not (2 <= base <= len(Lexer.BASE_CHARS)):
            self.__error(f"{self.linenum},{self.linepos}: Invalid integer base '{base}'")
            
        chars = Lexer.BASE_CHARS[0:base]
        
        num_string = ""
        
        while self.current_char and self.current_char.upper() in chars:
            num_string += self.current_char
            self.__advance()
        
        if self.current_char and self.current_char.isalpha():
            self.__error(f"{self.linenum},{self.linepos}: Integer '{num_string}' cannot be followed by alphabetic '{self.current_char}'.")
        
        return int(num_string, base=base)
        
    # Read a single character or escape sequence
    def __read_char(self):
        char = self.current_char
        
        # Check for escape sequence
        if char == "\\":
            self.__advance()
            
            if self.current_char == "a": # Bell
                char = '\a'
            elif self.current_char == "b": # Backspace
                char = '\b'
            elif self.current_char == "e": # Escape Character
                char = "\x1B"
            elif self.current_char == "f": # Form Feed
                char = '\f'
            elif self.current_char == "n": # Line Feed
                char = '\n'
            elif self.current_char == "r": # Carriage Return
                char = '\r'
            elif self.current_char == "t": # Horizontal Tab
                char = '\t'
            elif self.current_char == "v": # Vertical Tab
                char = '\v'
            elif self.current_char == "\\": # Backslash
                char = '\\'
            elif self.current_char == "'": # Single Quote
                char = '\''
            elif self.current_char == "\"": # Double Quote
                char = "\""
            elif self.current_char == "0": # Null
                char = "\0"
            
        self.__advance()
        return ord(char)
            
    # Read a sequence of single characters or escape sequences until a double quote is met
    def __read_string(self):
        string = []
        while self.current_char != "\"":
            string.extend(bytes(chr(self.__read_char()), encoding = "utf-8"))
            if self.current_char == None:
                self.__error(f"{self.linenum},{self.linepos-1}: Expected closing double quote while parsing string, got '{self.current_char or 'EOF'}'.")
            
        return string
    
    # Read any punctuator
    def __read_punctuator(self):
        punct_matches = []
        for punct in Lexer.PUNCTUATORS:
            if punct[0] == self.__peek(len(punct[0])):
                punct_matches.append(punct)
        
        if len(punct_matches) == 0:
            self.__error(f"{self.linenum},{self.linepos}: Invalid punctuator '{self.__peek(10)}{'{...}' if self.pos+10 < len(self.text) else '{EOF}'}'.")
        
        list.sort(punct_matches, key = lambda punct: len(punct[0]), reverse = True)
        punct = punct_matches[0]
        
        start = (self.linenum, self.linepos)
        
        [self.__advance() for _ in range(len(punct[0]))]
        
        return Token(punct[1], punct[0].strip(), start[0], start[1])
    
    def __get_next_token(self):
        while self.current_char is not None:
            
            # Ignore any comments
            if self.__peek(2) == "/*":
                comment_start = (self.linenum, self.linepos)
                while self.__peek(2) != "*/":
                    self.__advance()
                    if self.current_char == None:
                        self.__error(f"{comment_start[0]},{comment_start[1]}: Comment unclosed at end of file")
                del comment_start
            
            # Ignore any whitespace that isn't part of another structure
            elif self.current_char.isspace():
                self.__skip_whitespace()
                continue
            
            # Try parsing an integer if a digit is detected
            elif self.current_char.isdigit():
                start = (self.linenum, self.linepos)
                
                base = 10
                if self.current_char == '0':
                    if self.text[self.pos] and self.text[self.pos].isalpha():
                        self.__advance()
                        if self.current_char == "b":
                            base = 2
                        elif self.current_char == "o":
                            base = 8
                        elif self.current_char == "x":
                            base = 16
                        else:
                            self.__error(f"{self.linenum},{self.linepos-1}: Invalid base prefix '0{self.current_char}'")
                        self.__advance()
                
                num = self.__read_integer(base)
                
                return Token(Token.T_INT, num, start[0], start[1], wasChar = False)
            
            # Try parsing a character
            elif (self.current_char == "'"):
                start = (self.linenum, self.linepos)
                self.__advance()
                char_int = self.__read_char()
                
                # Check that it is closed by a single quote
                if self.current_char != "'":
                    self.__error(f"{self.linenum},{self.linepos-1}: Expected closing single quote while parsing character, got '{self.current_char or 'EOF'}'.")
                self.__advance()
                return Token(Token.T_CHAR, char_int, start[0], start[1], wasChar = True)
            
            # Try parsing a string
            elif (self.current_char == '"'):
                start = (self.linenum, self.linepos)
                self.__advance()
                utf8string = self.__read_string()
                self.__advance()
                return Token(Token.T_STR, utf8string, start[0], start[1])
            
            # Try parsing a name if a letter, _, ., or @ is encountered.
            elif (self.current_char.isalpha() and self.current_char.isascii()) or self.current_char in "_.@":
                return self.__read_name()
            
            # Try parsing a punctuator
            elif self.current_char in Lexer.PUNCTUATOR_CHARS:
                return self.__read_punctuator()
            
            # Otherwise, no valid token was found
            else:
                self.__error(f"{self.linenum},{self.linepos}: Unknown token start symbol '{self.current_char}'") 
            
            self.__advance()
        
        return Token(Token.T_EOF, None, self.linenum, self.linepos)
    
    def lex(self):
        tokens = []
        while True:
            token = self.__get_next_token()
            tokens.append(token)
            if token.type == Token.T_EOF:
                return tokens
            
    