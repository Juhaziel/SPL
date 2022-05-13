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

Prototype scoped variables are only checked against input when the input is a constant, known value.

In order for a file scoped variable to be visible to other files (program scoped), it must be prefixed by `global`.

During a function's definition, its parameters are set to block scope. Otherwise, the parameters are prototype scoped
Otherwise, prototype-scoped variables only last until the end of the procedure's declaration.

Program and file scoped variables are stored in the data segment and last the entire program's runtime.

Block scoped variables are stored in the stack of its corresponding function.
Alternatively, a block scoped variable may be declared in the data segment by prefixing it with `static`

#### 2.1.3 Types ####
