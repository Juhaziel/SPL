from sirlex import Token

class ProgramNode:
    def __init__(self):
        self.data_directives = []
        self.const_directives = []
        self.imports = []
        self.exports = []
        self.function_decls = []
    
    def __repr__(self):
        return f"Program(Data={len(self.data_directives)}, Const={len(self.const_directives)}, Import={len(self.imports)}, Export={len(self.exports)}, Function={len(self.function_decls)})"

class DataDirectiveNode:
    def __init__(self):
        self.data = []
    
    def __repr__(self):
        return f"Data(Datum={len(self.data)})"

class LabelNode:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Label({self.name})"

class DatumNode:
    def __init__(self, type):
        self.type = type
        self.allocsize = None
        self.data = []
    
    def __repr__(self):
        return f"Datum(Type={self.type}, Size={self.allocsize or len(self.data)}, Values={len(self.data)})"

class AlignNode:
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return f"Align(Boundary={self.type})"
        
class ConstantNode:
    T_SCONST = "SCONST"
    T_NAME = "NAME"
    T_STRING = "STRING"

    def __init__(self, type, data):
        self.type = type
        self.data = data
    
    def __repr__(self):
        value = self.data
        if self.type == ConstantNode.T_STRING:
            value = bytes(value).decode('utf8')
        return f"Constant({self.type}, {repr(value)})"

class FunctionDeclNode:
    def __init__(self):
        self.convention = None # Default Convention
        self.type = None
        self.name = ""
        self.fargs = []
        self.staticdata = None
        self.stmts = []
    
    def __repr__(self):
        return "Function(Convention={}, Type={}, Name={}, Args=({}), Static={}, Statements={})".format(
            self.convention or "Default",
            self.type or "None",
            self.name,
            ", ".join([x[0]+" "+x[1] for x in self.fargs]),
            self.staticdata or None,
            len(self.stmts)
        )

class EmptyStatement:
    pass
class DeclStatement:
    def __init__(self, type):
        self.type = type
        self.names = []
class DefStatement:
    def __init__(self, name, expr=None):
        self.name = name
        self.expr = expr
class MemWriteStatement:
    def __init__(self, type, addr_expr=None, val_expr=None):
        self.type = type
        self.addr_expr = addr_expr
        self.val_expr = val_expr
class IfStatement:
    def __init__(self, left=None, rel="!=", right=None):
        self.left = left
        self.rel = rel
        self.right = right
        self.if_block = []
        self.else_block = []
class GotoStatement:
    def __init__(self, name):
        self.name = name
class JumpStatement:
    def __init__(self, funct_expr=None):
        self.convention = None # Default calling convention
        self.funct_expr = funct_expr
        self.args = []
class CallStatement:
    def __init__(self, funct_expr=None):
        self.convention = None # Default calling convention
        self.type = None
        self.ret_register = None
        self.funct_expr = funct_expr
        self.args = []
class ReturnStatement:
    def __init__(self):
        self.expr = None

class ConstExpression:
    def __init__(self, const_node):
        self.const_node = const_node
class MemReadExpression:
    def __init__(self, type, addr_expr):
        self.type = type
        self.addr_expr = addr_expr
class UCastExpression:
    def __init__(self, type, expr):
        self.type = type
        self.expr = expr
class SCastExpression:
    def __init__(self, type, expr):
        self.type = type
        self.expr = expr
class BinaryExpression:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
class UnaryExpression:
    def __init__(self, op, value):
        self.op = op
        self.value = value

class ASTParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    def __error(self, text):
        raise Exception(f"[PARSER]: An error occured while parsing.\n{text}")

    # Assert that the next token is of a certain type
    def __eat(self, token_type, token_value=None):
        if self.current_token.type == token_type:
            if token_value and self.current_token.value != token_value:
                self.__error(f"{self.current_token.linenum},{self.current_token.linepos}: Expected '{token_value}' of type {token_type}, got '{self.current_token.value}'")
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = None
        else:
            self.__error(f"{self.current_token.linenum},{self.current_token.linepos}: Expected type '{token_type}', got '{self.current_token.type}'")

    # Tries parsing a top level program.
    # Returns a program node.
    def program(self):
        node = ProgramNode()

        while True:
            token = self.current_token
            if token.type == Token.T_EOF:
                return node
            
            elif token.type == Token.T_KEYWORD:
                if token.value == "data": # Try getting a data directive if 'data' appears
                    node.data_directives.append(self.__data())
                    
                elif token.value == "const": # Try getting a const directive if 'const' appears
                    self.__eat(Token.T_KEYWORD)
                    name = self.current_token.value
                    self.__eat(Token.T_NAME)
                    self.__eat(Token.T_ASSIGN)
                    value = self.__expr()
                    self.__eat(Token.T_SEMICOLON)
                    node.const_directives.append((name, value))
                    
                elif token.value == "import": # Try getting an import directive if 'import' appears
                    self.__eat(Token.T_KEYWORD)
                    node.imports.extend(self.__namelist())
                    self.__eat(Token.T_SEMICOLON)
                    
                elif token.value == "export": # Try getting an export directive if 'export' appears
                    self.__eat(Token.T_KEYWORD)
                    isWeak = False
                    if self.current_token.type == Token.T_KEYWORD and self.current_token.value == "weak":
                        isWeak = True
                        self.__eat(Token.T_KEYWORD)
                    node.exports.extend(map(lambda name: (name, isWeak), self.__namelist()))
                    self.__eat(Token.T_SEMICOLON)
                
                elif token.value == "foreign": # Try getting a function declaration if 'foreign' appears
                    node.function_decls.append(self.__functdecl())
                
                else:
                    self.__error(f"{token.linenum},{token.linepos}: Got unexpected keyword '{token.value}'")
                    
            else: # Otherwise it must be a function declaration
                node.function_decls.append(self.__functdecl())

    def __functdecl(self):
        node = FunctionDeclNode()

        # Parse convention if it exists
        node.convention = self.__conv()
        
        # Parse type or None
        self.__eat(Token.T_LPAR)
        if self.current_token.type == Token.T_TYPE:
            node.type = self.current_token.value
            self.__eat(Token.T_TYPE)
        self.__eat(Token.T_RPAR)

        # Parse function name
        node.name = self.current_token.value
        self.__eat(Token.T_NAME)

        # Parse formal argument list
        self.__eat(Token.T_LPAR)
        if self.current_token.type != Token.T_RPAR:
            node.fargs.extend(self.__farglist())
        self.__eat(Token.T_RPAR)

        # Parse static data
        if self.current_token.type == Token.T_KEYWORD and self.current_token.value == "data":
            node.staticdata = self.__data()

        # Parse statements
        node.stmts.extend(self.__block())

        return node
    
    def __data(self):
        node = DataDirectiveNode()
        self.__eat(Token.T_KEYWORD, "data")
        self.__eat(Token.T_LBRACE)
        while not (self.current_token.type == Token.T_RBRACE):
            node.data.append(self.__datum())
        self.__eat(Token.T_RBRACE)
        return node

    def __datum(self):
        if self.current_token.type == Token.T_NAME: # Parse Label
            return self.__label()

        elif self.current_token.type == Token.T_ALIGN: # Parse Align directive
            align = self.current_token.value
            self.__eat(Token.T_ALIGN)
            self.__eat(Token.T_SEMICOLON)
            return AlignNode(align)

        elif self.current_token.type == Token.T_TYPE: # Parse data declaration
            type = self.current_token.value
            self.__eat(Token.T_TYPE)
            node = DatumNode(type)

            if self.current_token.type == Token.T_LBRACKET: # Get allocation size
                self.__eat(Token.T_LBRACKET)
                if self.current_token.type != Token.T_RBRACKET:
                    node.allocsize = self.__expr()
                self.__eat(Token.T_RBRACKET)
            else:
                node.allocsize = ConstExpression(ConstantNode(ConstantNode.T_SCONST, 1))
            
            if self.current_token.type == Token.T_STR: # Get string
                if type != "word1":
                    self.__error(f"{self.current_token.linenum},{self.current_token.linepos}: String in data declaration expected type 'word1', got type '{type}'")
                if node.allocsize != None:
                    self.__error(f"{self.current_token.linenum},{self.current_token.linepos}: String in data declaration expected empty allocation size, got expression.")
                node.data.extend([ConstExpression(ConstantNode(ConstantNode.T_SCONST, x)) for x in self.current_token.value])
                node.data.append(ConstExpression(ConstantNode(ConstantNode.T_SCONST, 0))) # Append a final 0
                self.__eat(Token.T_STR)
            
            elif self.current_token.type == Token.T_LBRACE: # Or get initialisation data
                self.__eat(Token.T_LBRACE)
                node.data.extend(self.__exprlist())
                self.__eat(Token.T_RBRACE)
            
            else:
                if node.allocsize == None:
                    self.__error(f"{self.current_token.linenum},{self.current_token.linepos}: Datum allocation size must be explicitly stated, got empty allocation.")
            
            if node.allocsize == None:
                node.allocsize = ConstExpression(ConstantNode(ConstantNode.T_SCONST, max(1, len(node.data))))
            
            self.__eat(Token.T_SEMICOLON)
            return node
        
        else:
            self.__error(f"{self.current_token.linenum},{self.current_token.linepos}: Got unexpected symbol '{self.current_token}'.")

    def __label(self):
        name = self.current_token.value
        self.__eat(Token.T_NAME)
        self.__eat(Token.T_COLON)
        return LabelNode(name)

    def __const(self):
        type = None
        value = self.current_token.value
        if self.current_token.type == Token.T_INT:
            self.__eat(Token.T_INT)
            type = ConstantNode.T_SCONST
        elif self.current_token.type == Token.T_NAME:
            self.__eat(Token.T_NAME)
            type = ConstantNode.T_NAME
        elif self.current_token.type == Token.T_STR:
            self.__eat(Token.T_STR)
            type = ConstantNode.T_STRING
        else:
            self.__error(f"{self.current_token.linenum},{self.current_token.linepos}: Expected constant, got '{self.current_token.type}'")
        return ConstantNode(type, value)

    def __conv(self):
        convention = None
        if self.current_token.type == Token.T_KEYWORD and self.current_token.value == "foreign":
            self.__eat(Token.T_KEYWORD)
            convention = self.current_token.value
            self.__eat(Token.T_NAME)
        return convention

    def __block(self):
        stmts = []
        self.__eat(Token.T_LBRACE)
        while self.current_token.type != Token.T_RBRACE:
            stmts.append(self.__stmt())
        self.__eat(Token.T_RBRACE)
        return stmts

    def __stmt(self):
        if self.current_token.type == Token.T_KEYWORD:
            keyword = self.current_token.value
            if keyword not in ["foreign"]:
                self.__eat(Token.T_KEYWORD)

            if keyword == "pass": # Empty Statement
                self.__eat(Token.T_SEMICOLON)
                return EmptyStatement()
            elif keyword == "goto": # Local jump
                goal = self.current_token.value
                self.__eat(Token.T_NAME)
                self.__eat(Token.T_SEMICOLON)
                return GotoStatement(goal)
            elif keyword == "return": # Return statement
                node = ReturnStatement()
                if self.current_token.type != Token.T_SEMICOLON:
                    node.expr = self.__expr()
                self.__eat(Token.T_SEMICOLON)

                return node
            elif keyword == "if": # Selection statement
                node = IfStatement()

                self.__eat(Token.T_LPAR)
                node.left = self.__expr()
                
                if self.current_token.type != Token.T_RPAR:
                    node.rel = self.current_token.value
                    self.__eat(Token.T_RELOP)
                    node.right = self.__expr()
                else:
                    node.rel = "!="
                    node.right = ConstExpression(ConstantNode(ConstantNode.T_SCONST, 0)) # Default to "left != false"
                self.__eat(Token.T_RPAR)

                node.if_block = self.__block()

                if self.current_token.type == Token.T_KEYWORD and self.current_token.value == "else":
                    self.__eat(Token.T_KEYWORD)
                    node.else_block = self.__block()
                
                return node
            elif keyword == "jump": # Function jump, default convention
                node = JumpStatement()

                node.funct_expr = self.__expr()
                self.__eat(Token.T_LPAR)
                if self.current_token.type != Token.T_RPAR:
                    node.args.extend(self.__exprlist())
                self.__eat(Token.T_RPAR)
                self.__eat(Token.T_SEMICOLON)

                return node
            elif keyword == "foreign":
                conv = self.__conv()

                if self.current_token.type == Token.T_LPAR: # Function call, explicit convention
                    node = CallStatement()
                    node.convention = conv

                    self.__eat(Token.T_LPAR)
                    if self.current_token.type != Token.T_RPAR:
                        node.type = self.current_token.value
                        self.__eat(Token.T_TYPE)
                    self.__eat(Token.T_RPAR)

                    if self.tokens[self.pos+1].type == Token.T_ASSIGN:
                        node.ret_register = self.current_token.value
                        self.__eat(Token.T_NAME)
                        self.__eat(Token.T_ASSIGN)
                    
                    node.funct_expr = self.__expr()
                    self.__eat(Token.T_LPAR)
                    if self.current_token.type != Token.T_RPAR:
                        node.args.extend(self.__exprlist())
                    self.__eat(Token.T_RPAR)
                    self.__eat(Token.T_SEMICOLON)

                    return node
                elif self.current_token.type == Token.T_KEYWORD and self.current_token.value == "jump": # Function jump, explicit convention
                    node = JumpStatement()
                    node.convention = conv

                    node.funct_expr = self.__expr()
                    self.__eat(Token.T_LPAR)
                    if self.current_token.type != Token.T_RPAR:
                        node.args.extend(self.__exprlist())
                    self.__eat(Token.T_RPAR)
                    self.__eat(Token.T_SEMICOLON)
                    
                    return node
            
        elif self.current_token.type == Token.T_LPAR: # Function call, default convention
            node = CallStatement()

            self.__eat(Token.T_LPAR)
            if self.current_token.type != Token.T_RPAR:
                node.type = self.current_token.value
                self.__eat(Token.T_TYPE)
            self.__eat(Token.T_RPAR)

            if self.tokens[self.pos+1].type == Token.T_ASSIGN:
                node.ret_register = self.current_token.value
                self.__eat(Token.T_NAME)
                self.__eat(Token.T_ASSIGN)
                    
            node.funct_expr = self.__expr()
            self.__eat(Token.T_LPAR)
            if self.current_token.type != Token.T_RPAR:
                node.args.extend(self.__exprlist())
            self.__eat(Token.T_RPAR)
            self.__eat(Token.T_SEMICOLON)

            return node

        elif self.current_token.type == Token.T_NAME:
            if self.tokens[self.pos+1].type == Token.T_COLON: # Local label definition
                return self.__label()
            
            name = self.current_token.value
            self.__eat(Token.T_NAME)
            if self.current_token.type == Token.T_ASSIGN: # Variable ssignment statement
                node = DefStatement(name)
                self.__eat(Token.T_ASSIGN)
                node.expr = self.__expr()
                self.__eat(Token.T_SEMICOLON)
                return node
            else:
                self.__error(f"{self.current_token.linenum},{self.current_token.linepos}: Got unexpected token '{self.current_token}'.")
                        
        elif self.current_token.type == Token.T_TYPE:
            type = self.current_token.value
            self.__eat(Token.T_TYPE)
            if self.current_token.type == Token.T_LBRACKET: # Memory write statement
                node = MemWriteStatement(type)

                self.__eat(Token.T_LBRACKET)
                node.addr_expr = self.__expr()
                self.__eat(Token.T_RBRACKET)

                self.__eat(Token.T_ASSIGN)
                node.val_expr = self.__expr()
                self.__eat(Token.T_SEMICOLON)

                return node
            elif self.current_token.type == Token.T_NAME: # Declaration
                node = DeclStatement(type)
                node.names.extend(self.__namelist)
                self.__eat(Token.T_SEMICOLON)

                return node
            else:
                self.__error(f"{self.current_token.linenum},{self.current_token.linepos}: Got unexpected token '{self.current_token}'.")

        else:
            self.__error(f"{self.current_token.linenum},{self.current_token.linepos}: Got unexpected token '{self.current_token}'.")

    def __expr(self):
        unary_ops = ["-"]
        binary_ops = {
            '|': 1, '~|': 1,
            '^': 2, '~^': 2,
            '&': 3, '~&': 3,
            '<<': 4, '>>': 4, '>>$': 4,
            '+': 5, '-': 5,
            '*': 6, '/': 6, '/$': 6, '%': 6
        }

        def get_atom():
            if self.current_token.type == Token.T_EOF: # Error on end of file
                self.__error(f"{self.current_token.linenum},{self.current_token.linepos}: Expected expression, got EOF.")
            
            elif self.current_token.type in [Token.T_INT, Token.T_NAME, Token.T_STR]: # Get constant integer
                return ConstExpression(self.__const())

            elif self.current_token.type == Token.T_LPAR: # Get sub expression
                self.__eat(Token.T_LPAR)
                expr = self.__expr()
                self.__eat(Token.T_RPAR)
                return expr
            
            elif self.current_token.type == Token.T_TYPE:
                type = self.current_token.value
                self.__eat(Token.T_TYPE)
                if self.current_token.type == Token.T_LBRACKET: # Memory write
                    self.__eat(Token.T_LBRACKET)
                    addr_expr = self.__expr()
                    self.__eat(Token.T_RBRACKET)
                    return MemReadExpression(type, addr_expr)
                
                elif self.current_token.type == Token.T_LPAR: # Unsigned type
                    self.__eat(Token.T_LPAR)
                    expr = self.__expr()
                    self.__eat(Token.T_RPAR)
                    return UCastExpression(type, expr)
                
                elif self.current_token.type == Token.T_SIGNED: # Signed type
                    self.__eat(Token.T_SIGNED)
                    self.__eat(Token.T_LPAR)
                    expr = self.__expr()
                    self.__eat(Token.T_RPAR)
                    return SCastExpression(type, expr)
                
                else:
                    self.__error(f"{self.current_token.linenum},{self.current_token.linepos}: Got unexpected token '{self.current_token}'.")

            elif self.current_token.type == Token.T_OP and self.current_token.value in unary_ops: # Get unary
                op = self.current_token.value
                self.__eat(Token.T_OP)
                value = get_atom()
                return UnaryExpression(op, value)

            else:
                self.__error(f"{self.current_token.linenum},{self.current_token.linepos}: Got unexpected token '{self.current_token}'.")

        def get_expr(min_prec):
            result = get_atom()

            while self.current_token.type == Token.T_OP and binary_ops.get(self.current_token.value, -1) >= min_prec:
                op = self.current_token.value
                prec = binary_ops.get(op)
                self.__eat(Token.T_OP)
                rhs = get_expr(prec + 1)
                result = BinaryExpression(result, op, rhs)
            
            return result

        return get_expr(1)

    def __namelist(self):
        names = []
        while True:
            names.append(self.current_token.value)
            self.__eat(Token.T_NAME)
            if self.current_token.type == Token.T_COMMA:
                self.__eat(Token.T_COMMA)
            else:
                break
        return names

    def __exprlist(self):
        exprs = []
        while True:
            exprs.append(self.__expr())
            if self.current_token.type == Token.T_COMMA:
                self.__eat(Token.T_COMMA)
            else:
                break
        return exprs

    def __farglist(self):
        fargs = []
        while True:
            type = self.current_token.value
            self.__eat(Token.T_TYPE)
            name = self.current_token.value
            self.__eat(Token.T_NAME)
            fargs.append((type, name))
            if self.current_token.type == Token.T_COMMA:
                self.__eat(Token.T_COMMA)
            else:
                break
        return fargs