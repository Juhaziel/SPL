# Solar Programming Language (SPL) #

## 1. Description ##

The Solar Programming Language (SPL) is a C-like, procedural, unsafe, statically and explicitly typed language.
It was designed initially for the homebrew Mercury instruction set with plans to be compilable for other homebrew CPUs.
SPL is simply an amateur experiment with compilation and a tool made to test simple homebrew CPUs.

This Git repository contains documentation on SPL as well as a compiler toolchain with a Mercury Assembly backend

## 2. Language ##

### 2.1 Concepts ###

#### 2.1.1 Namespaces ####
A namespace is a dictionary mapping unique identifiers to their respective object.
Just like C, there are 4 namespaces:

	- Labels (loop names)
	- Tags (names of structures, enums and unions)
	- Members of structs and unions (each struct/union has its own namespace)
	- Everything else

#### 2.1.2 Scopes ####
A singular program can be divided into multiple scopes that each maintain their own set of identifiers.
Scope specify what namespaces are currently visible and follow a stack structure.

The scope of an identifier is the scope of its declaration, not its definition.
An identifier may be declared multiple times in the same scope, but it must not be defined more than once within the same scope level.
Definitions in a lower (inner) scope will hide higher (outer) scoped identifiers of the same type.
As such, inner scopes take precedence over higher ones.

The possible scope levels are:
	
	- Program Scope (All files being compiled together)
	- File Scope (All identifiers in the current source file that are not prototype or block scoped)
	- Block Scope (Inside procedures or blocks)
	- Prototype Scope (Inside procedure declarations)

In order for a file scoped variable to be visible to other files (program scoped), its indicator must be set to `global`).

The value of any program or file scoped variable must not be the return value of a procedure.
In other words, it must either be uninitialized or set to a literal value

During a procedure's definition, its parameters are set to block scope. Otherwise, the parameters are prototype scoped
Otherwise, prototype-scoped variables only last until the end of the procedure's declaration.

Program and file scoped variables are stored in the data segment and last the entire program's runtime.

Block scoped variables are stored in the stack of its corresponding procedure.
Alternatively, a block scoped variable may be declared in the data segment by setting its indicator to `static`

#### 2.1.3 Types ####
SPL features these basic types:
	
	(INTEGERS)
	- int (macro-defined INT_TYPE_SIZE, should represent 1 word)
	- int8 (1 byte signed)
	- int16 (2 bytes signed)
	- int32 (4 bytes signed)
	- int64 (8 bytes signed)
	and their unsigned equivalents prefixed by `u` (uint8, uint16, uint32, uint64)
	
	(FLOATS)
	- half (2 byte half-float IEEE 754)
	- float (4 byte float IEEE 754)
	- double (8 byte float IEEE 754)

More complex types can be created such as:

	- An array type representing a contiguous array of elements of the same type.
	- A pointer type representing the address of another variable.
	- A structure type representing a grouping of many values.
	- An union type representing an overlap of multiple variables.
	- A procedure type representing a block of instructions that can be called with varying parameters and returns a value (or void if none). 

The sizes all basic types and pointers are known.
Arrays, structures and unions can be incomplete if:

	- A structure or union was declared but not defined.
	- An array was declared without a size and was not defined.

An array definition does not need to specify its size in the declaration as it can be inferred
from the size of the right side of the equal sign.

Unlike C, variable length arrays are strictly forbidden and must be dynamically allocated.
This means an expression such as `arr [n]uint16` where n is an unknown variable is not allowed.
However, that expression will work if n has a value known at compile time.

A pointer can point to *void* and still be valid as it is internally a singular number.
Such pointers can be implicitly casted to any and all other type of pointer.

Procedures are special in that they are not first-class members.
As such, they cannot be returned from procedures nor passed to them.
Instead, procedure pointers **must** be used to pass a procedure by reference.

##### 2.1.3.1 Type Storage Specifiers #####
SPL possesses two storage specifying keywords:
	
	- global, indicates a file scoped variables must be elevated to program scope.
	- static, indicates a block scoped variable must be stored statically in the data segment.

##### 2.1.3.2 Type Qualifiers #####
A variable can be qualified by two keywords:

	- volatile, indicates a variable may be changed by an external program.
	- const, indicates the current program must not change this variable.

### 2.2 Lexical Elements ###
A token consists of:

	- keyword
	- identifier
	- constant
	- string
	- punctuator

A pre-processing token consists of:

	- identifier
	- number
	- char
	- string
	- punctuator
	- other

Any token that does not fall within the pre-processing tokens becomes an *other* token.

#### 2.2.1 Keywords: ####
|          |        |         |          |
|----------|--------|---------|----------|	
| break    | for    | static  | void     |
| const    | global | struct  | volatile |
| continue | if     | typedef |          |
| else     | return | union   |          |
| enum     | sizeof | var     |          |

plus all the variable types

#### 2.2.2 Identifier ####
An identifier is a string of ASCII alphanumerical characters including the underscore.
It **must not** begin with a number

#### 2.2.3 Constants ####
A constant can either be an integer, a floating point number, an enum identifier or a single ASCII character.

##### 2.2.3.1 Integer constant #####
Can be either:
	
	- A decimal number (starting with a non-zero digit)
	- A binary number (starting with 0b)
	- A hexadecimal number (starting with 0x)

And can be preceded by a negative sign.

##### 2.2.3.2 Floating point constant #####
Can be either:
	
	- A regular decimal fraction (mandatory .)
	- A hexadecimal fraction (starting with 0x, mandatory .)
	- A binary fraction (starting with 0b, mandatory .)
	- A scientific notation equivalent with the appropriate prefix, a mantissa (fractional or decimal), e or E and a signed exponent.

##### 2.2.3.3 Enum constant #####
This is simply an identifier. It will be verified by the parser and its semantic analyzer.

##### 2.2.3.4 ASCII constant #####
Enclosed within single quotes (').
Can be either:
	
	- A single ASCII character that is not ', \ or a new line
	- An escape sequence:
		- \', \", \\\\, \a, \b, \f, \r, \n, \t, \v
		- \xXX (where XX is an hexadecimal byte)

#### 2.2.4 String literal ####
Enclosed within double quotes (")
Can be a sequence of:

	- Single ASCII characters that is not ", \ or a new line
	- An escape sequence like ASCII constants.

Adjacent string literal tokens will be combined.

#### 2.2.5 Punctuators ####
Covers all punctuation useful to SPL in the ASCII set
```
[ ] ( ) { } . ->
& * + - ~ !
/ % << >> < > <= >= == != ^ | && ||
@ ? : ;
= *= /= %= += -= <<= >>= &= ^= |=
, # ## 
```

#### 2.2.6 Preprocessor numbers ####
Since the preprocessor does not care for number types, it uses simplified lexing rules.

A number recursively is defined as an optional prefix (0x, 0b) followed by:
	
	- A sequence of digits (hexadecimal, decimal or binary)
	- A number followed by a point
	- A number followed by e or E and a sign (+ or -)

### 2.3 Expressions ###
Expressions are sequences of operands and operators that computes a value and/or designates an entity and/or generates side effects.

Precedence of operators is verified through syntax but associativity is not.
As such, left-associative expressions must be corrected by the parser.

#### 2.3.1 Primary expressions ####
Can either be:

	- identifier
	- constant
	- string-literal
	- ( expression )

#### 2.3.2 Postfix expressions ####
Can either be:

	- primary-expression
	- postfix-expression [ expression ]
	- postfix-expression ( argument-expression-list )
	- postfix-expression . identifier
	- postfix-expression -> identifier

##### 2.3.2.1 Array indexing #####
Given an array `arr`, the expression `arr[n]` indexes the nth index of arr.
This is equivalent to the operation `*((arr)+(n * sizeof(arr[0])))`
i.e. the index is multiplied by the size of the elements of *arr* and is then added to *arr*, which is the address of the first element of *arr*.

This expression evaluates to the same type as the elements of the array.

##### 2.3.2.2 Procedure calls #####
A postfix expression that resolves to a procedure **or** a procedure pointer and that is followed by either
empty parentheses or parentheses enclosing a comma-separated set of expressions will call the associated
procedure with the contents of the parentheses.

This expression evaluates to the return type of the procedure.
If it is void, any attempt to modify or access the return value is undefined behaviour.

##### 2.3.2.3 Structure and union members #####
The first operand of . must be a *struct* or *union*
The first operand of -> must be a pointer to a *struct* or *union*

In both cases, the second operand must be a member of the corresponding *struct* or *union*

#### 2.3.3 Unary operators ####
Can either be:
	
	- postfix-expression
	- unary-operator cast-expression
	- sizeof unary-expression
	- sizeof ( var-type )

##### 2.3.3.1 Unary operators #####
Can either be:
	
	- & (address-of operator, returns a pointer)
	- \* (dereference operator, returns an element of the pointer's type)
	- + (unary plus, number only)
	- - (unary minus, number only)
	- ~ (bitwise not, integer only)
	- ! (logical not, number only)

##### 2.3.3.2 The sizeof operator #####
sizeof cannot be applied to incomplete types (undefined arrays, structures, unions)
nor can it be applied to procedures.

sizeof returns the size in bytes of an expression or a variable type.

##### 2.3.3.3 Cast operator #####
Can be either:

	- unary-expression
	- ( var-type ) cast-expression

The cast expression must be basic or pointer based
The expression is converted to the type in between the parentheses.
