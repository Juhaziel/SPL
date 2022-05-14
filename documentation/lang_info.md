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

In general, the sizes all basic types, structures, unions, pointers and arrays are known.
Unlike C, variable length arrays are strictly forbidden and must be dynamically allocated.
This means an expression such as `arr [n]uint16` where n is an unknown variable is not allowed.
However, that expression will work if n has a value known at compile time.

Procedures are special in that they are not first-class members.
As such, they cannot be returned from functions nor passed to them.
Instead, function pointers **must** be used to pass a function by reference.

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

2.2.1 Keywords:

|          |        |         |          |
|----------|--------|---------|----------|	
| break    | for    | static  | void     |
| const    | global | struct  | volatile |
| continue | if     | typedef |          |
| else     | return |  union  |          |
| enum     | sizeof | var     |          |

plus all the variable types