# Solar IR (SIR) #

## 1 Introduction ##

Solar IR aims to be an adaptation of C-- to serve as intermediate representation of SPL code. It is currently an abstraction of the Mercury assembly language.

Source code is written using ASCII or UTF-8 (for unicode)

## 2 Syntax ##

### 2.1 Grammar ###

```
Program
	program
		: EOF
		| pad program+
		;

PAD
	pad
		: data
		| conv? '(' TYPE? ')' NAME '(' farglist ')' data? block
		| 'import' namelist ';'
		| 'export' 'weak'? namelist ';'
		| 'const' NAME '=' expr;
		;

Data
	data
		: 'data' '{' datum* '}'
		;

Datum
	datum
		: NAME ':'
		| TYPE ('[' expr? ']')? ('{' exprlist? '}')? ';'
		| 'word1' '[' ']' STRING ';'
		| ALIGNN ';'
		;
		
Constants
	const
		: INT | CHAR
		| NAME
		| STRING
		;

Convention
	conv
		: 'foreign' CONVKIND
		;
		
Block
	block
		: '{' stmt* '}'
		;
		
Statements
	stmt
		: 'pass' ';'
		| TYPE namelist ';'
		| NAME '=' expr ';'
		| TYPE '[' expr ']' '=' expr ';'
		| 'if' '(' expr rel expr ')' block ('else' block)?
		| NAME ':'
		| 'goto' NAME ';'
		| conv? 'jump' expr '(' exprlist? ')' ';'
		| conv? '(' TYPE? ')' (name '=')? expr '(' exprlist? ')' ';'
		| 'return' expr? ';'
		;

Expressions
	expr
		: const
		| TYPE '[' expr ']'
		| '(' expr ')'
		| TYPE '(' expr ')'
		| TYPE '$' '(' expr ')'
		| expr op expr
		| '-' expr
		;

Operators
	op
		: '+' | '-' | '*' | '/' | '/$' | '%' | '%$'
		| '&' | '|' | '^' | '~&' | '~|' | '~^'
		| '<<' | '>>' | '>>$'
		;

Relations
	rel
		: '==' | '!=' 
		| '>' | '<' | '>=' | '<='
		| '>$' | '<$' | '>=$' | '<=$'
		;

Name List
	namelist
		: NAME (',' namelist)?
		;

Expression List
	exprlist
		: expr (',' exprlist)?
		; 
		
Formal Arguments
	farglist
		: TYPE NAME (',' farglist)?
		;

```

#### 2.2.1 Keywords ####

|        |         |        |        |       |
|--------|---------|--------|--------|-------|
| align1 | const   | goto   | pass   | word1 |
| align2 | data    | if     | ptr    | word2 |
| align4 | else    | import | return | word4 |
| align8 | export  | jump   | weak   | word8 |
| alignp | foreign |        |        |       |

#### 2.2.2 Terminals ####

- **NAME**: A string of 8-bit characters that must start with an ASCII letter.
- **TYPE**: A variable type of format `wordN`, where N is the number of word.
- **INT**: An integer value, signed or unsigned.
- **CHAR**: An integer value represented by a textual character.
- **STRING**: An array of `word1` characters, string encoded as UTF-8
- **ALIGNN**: An align directive, to an N word boundary
- **CONVKIND**: A kind of calling convention.

### 2.3 Concepts ###

#### 2.3.1 Comments ####

Comments are surrounded by `/*` and `*/`, and are discarded at the lexer level. They cannot be nested.

**EXAMPLE**
`/* this is a comment */`

#### 2.3.2 Names ####

Names, or identifiers, must begin with an ASCII letter, a dot (`.`), a at sign (`@`), or an underscore (`,`), and they are case-sensitive. They are identifiers for registers or memory addresses.

Keywords can be used as names **only if** they are preceded by the `@` symbol. The symbol will then be stored internally with the preceding `@` stripped off.

Names cannot contain ASCII control characters, spacing characters, nor punctuators in the ASCII range (except `@`). They must only contain characters considered lettering in any Unicode-supported language.

Unicode names will be encoded as UTF-8.

##### 2.3.2.1 Punctuation #####
Solar IR reserves the use of certain punctuators.
```
( ) { } [ ]
; : ,
== != < > <= >=
+ - * / %
& | ^ ~ << >>
= !
/* */
$
```

Solar IR also reserves these punctuators for future expansion
```
# ## ?
```

As such, these punctuators cannot be used in names.

#### 2.3.3 Types ####

Only integers (`wordN`) are available to Solar IR, and they are defined by their size `N` in words (not bytes).

- The size N of `wordN` can be 1, 2, 4, or 8 words
- The special keyword `ptr` has the address bus' size

##### 2.3.3.1 Base Prefix #####

Integer literals can be preceded by an optional base prefix. All of these prefixes begin with 0. As such, a number literal cannot begin with 0 if it is not prefixed.

- `0b`: binary
- `0o`: octal
- no prefix: decimal (must not begin with 0)
- `0x`: hexadecimal

#### 2.3.4 Constants ####

Constants, or literals, are signed or unsigned integers, characters, strings, or names.

##### 2.3.4.1 Integers #####

Integers are of the widest type, `word8`. Casting may be used to manually restrict the type of an integer literal.

##### 2.3.4.2 Characters and Strings #####

Characters are interpreted exactly as an integer where the value is that character's Unicode codepoint. They are enclosed within single quotes (`'`)
   
Strings literals are a list of `word1` corresponding to its character's individual UTF-8 values, followed by a terminating null word. Strings correspond to an`ptr` type constant. The value of this `ptr` will be the starting address of the array of `word1` defined in an anonymous data segment.

#### 2.3.5 Memory ####

Memory is directly accessible as an array of words from which different sized types can be read or written. The size of addressable memory depends on the width of `word`. All addresses and offsets into memory are defined in words (the width of `word1`)

Endianness is not guaranteed on types wider than `word1`

#### 2.3.6 Import and Export ####

Named memory addresses can be imported from other object files using the `import` statement. Labels of data and fonctions defined in the program file can also be exported using the `export` and `export weak` statements.

`export weak` allows later redefinitions, while `export` does not redefine a label once it has been defined

It is safer to export functions whose calling conventions have been explicitly defined, as the compiler's implicit convention may change between versions.

Names that are imported or exported this way are guaranteed to remain unchanged. On the contrary, the actual names of local symbols may be reassigned.

#### 2.3.7 Constant directive ####

The `const` directive allows defining compile-time constants that will not be stored within memory.
They must evaluate to a constant.

#### 2.3.8 Data Segment ####

The data segment contains all static data defined by a program and is created at compile time.

#### 2.3.9 Code Segment ####

The code segment contains all executable code generated by a program and is created at compile time.

#### 2.3.10 Registers ####

A register, or local variable, is a named variable defined within a function. Registers are available in an endless supply and should not be seen as having an address.

#### 2.3.11 Local Labels ####

Local labels can be declared within a function body similarly to data labels. However, these local labels are only usable in `goto` expressions. They are not memory addresses and are not registers.

#### 2.3.12 Scoping and Namespaces ####

Names exist in two scopes: global and local. Global names refer to datum and functions, and their value is the memory address. Local names can refer to registers or local labels, the first of which takes priority over global names.

Only registers can have their value overwritten.

Local labels exist within their own namespace and as such are independent from register or global .

#### 2.3.13 Calling Conventions ####

To support interoperability with other object files, Solar IR also supports declaring a specific calling convention for function calls or parametrized jumps.

The current calling conventions are:

**C**:
	Push arguments on stack from right to left.
	Caller assigns space on stack for return value before call.
	Caller cleans up stack after call.

**MS**:
	Push arguments on stack from right to left.
	Caller assigns space on stack for return value before call.
	Callee cleans up stack before return.

If no explicit calling convention is specified, the compiler will use its own. As the particular implementation is compiler specific, only functions with explicitly declared calling conventions should be exported.

## 3 Data Layout ##

Static data is defined using the `data` directive. The data segment of the data directive is a contiguous array of words, the length of which is defined by its datum declarations. Each value can be initialized or not.

There can be any number of data directives within a program. However, as the layout between different data segments is implementation-specific, memory operations on them should stay within bounds of the data segment.

Each datum of the data directive will be enclosed within the data directive's braces (`{}`).

```
data {
	datum1
	datum2
	...
	datumN
}

(N >= 0)
```

### 3.1 Labels ###

A label can be considered as a pointer to a memory address and are of type `ptr`. Once declared, they become names that can be used in expressions. Labels can be used before they are declared. They cannot be modified but are not considered constant expressions.

A label points to the first word of the first datum declared after itself.

To declare a label, it suffices to follow a regular name with a colon (':')

```
data {
	label1:
		datum
		...
	label2:
		datum
		...
}
```

### 3.2 Initialisation ###

To allocate memory for a datum, the type, amount of elements must be specified. The amount of elements must be greater than 0 and must be enclosed within brackets (`[]`). The amount of elements must be a constant expression.

Additionally, a comma-separated list of constant expressions enclosed within braces (`{}`) called `{constant-list}` can be provided for initialisation values.

There are many variants:

1. If `[N]` is not provided, only one element is allocated.
	It may be followed by a `{constant-list}` containing a singular element.
	If no initial value is provided, the value is undefined.
	
2. If `[N]` is provided, then `N` elements are allocated.
	It may be followed by a `{constant-list}` of `C` items, where 1 <= C <= N.
	Element `i`, 1 <= `i` <= `N`, will be initialized to `i mod C` .
	
3. If `N = C`, then `[N]` may be safely replaced by `[]`.
	If the type is `word1`, then the `{constant-list}` can be replaced by a string.

The endianess of multi-word values is not guaranteed and may vary if the original type is not used.

### 3.3 Alignment ###

A datum can be replaced by an `alignN` directive, where N is 1, 2, 4, 8 for the number of words, or p the size of `ptr`. This directive will add the required number of padding zeroes to ensure that the following datum is aligned.

## 4 Functions ##

Executable code is defined by function declarations. These declarations specify a calling convention, a return type, a name, arguments, and code. Static data bound locally to the function can also be specified using a special data directive.

Apart from the name and code, all other elements are optional.

### 4.1 Function Definition ###

A function definition has the following syntax:

```
conv ( type ) func_name ( arg1, ..., argN )
data { datum1, ..., datum2 }
{ body }
```

#### 4.1.1 Convention ####
An explicit calling convention can be introduced with the `foreign` keyword followed by a convention name. If there is no explicit calling convention, `conv` is left empty and the compiler's implicit calling convention will be used.

#### 4.1.2 Return Value ####
A function can return only one value, whose type is specified by `type` If there is no return value, then `type` is left empty and only the parenthesis (`()`) are kept.

#### 4.1.3 Formal Arguments ####
A formal argument is defined by a type and then a name. The complete argument list is separated by commas and is placed within parenthesis (`()`) after `func_name`.

Every argument's name is locally available to statements in the function body.

#### 4.1.4 Static Data ####
Static data local to this function can be declared using the same syntax as the data directive. This data directive is placed between the function header and its body. If there is not static data, the entire directive can be left out.

Every label defined within this data directive is locally available to statements in the function body.

#### 4.1.5 Body Block ####
The body is an arbitrary amount of statements encased within braces (`{}`), otherwise known as a *block*.

#### 4.2 Statements ####

##### 4.2.1 `pass` #####

This statement is the null statement, with no effects. Its main use is for clarity.

##### 4.2.2 Declaration #####

A declaration statement has the following syntax:
```
type name1, ..., nameN ;
```

This statement declares local names as registers of type `type`. Register names cannot be used before they are declared, and names cannot be redeclared. These declared local names take precedence over global names, but must be unique within the function's body.

##### 4.2.3 Assignment #####

An assignment statement has the following syntax:
```
name = expr ;
```

This statement assigns `expr`'s value to a previously declared local name (register).

`expr`'s value will be **truncated** or **zero-extended** to `type`'s actual size limit.

##### 4.2.4 Memory Write #####

A memory write statement has the following syntax:
```
type [ addr_expr ] = val_expr ;
```

This statement writes `val_expr`'s value to the memory address returned by evaluating `addr_expr`.

`val_expr`'s value will be **truncated** or **zero-extended** to `type`'s actual size limit.

`addr_expr`'s value will be **truncated** or **zero-extended** to the `ptr` type's actual size limit.

##### 4.2.5 `if` #####

A selection (`if`) statement has the following syntax:
```
if ( expr1 rel expr2 ) { if_body } else { else_body }
```

The `else` branch is optional and may be left empty.

The selection statement serves as the only conditional statement of Solar IR. Loops can be implemented using `goto` and local labels.

To compare its two expressions, the selection statements uses a relational operator `rel`. These operators are not available to expressions.

This is the set of relational operators:

| rel | Relation                  |
|-----|---------------------------|
| ==  | Equal                     |
| !=  | Not equal                 |
| >   | Unsigned Greater          |
| <   | Unsigned Smaller          |
| >=  | Unsigned Greater or equal |
| <=  | Unsigned Smaller or equal |
| >$  | Signed Greater Unsigned   |
| <$  | Signed Smaller            |
| >=$ | Signed Greater or equal   |
| <=$ | Signed Smaller or equal   |

If the condition evaluates to true, the block of statements of `if_body` will be executed. Otherwise, if an else branch has been defined, it will execute `else_body`.

##### 4.2.6 Local labels and `goto` #####

Local labels paired with the `goto` statement allows altering the flow of the program. Local labels are declared by suffixing a `name` with a colon (`:`) like data directive labels. However, unlike data and function labels, these local labels do not represent memory addresses and can only be used with `goto` statements.

Therefore, a `goto` statement may only take a local label as argument and transfers control to that label.

A `goto` statement has the following syntax:
```
goto label ;
```

Local labels are in a different namespace than global and local variables, so overlap between names is acceptable.

**EXAMPLE**

The following is `for` loop from 0 to 9 using the selection, label and `goto` statements.

```
...
for (int i = 0; i < 10; i++) {
	printi(i);
}
...
```
is replaced by
```
...
word1 i;
i = 0;
start: if (i < 10) {
	printi(i);
	i = i + 1;
	goto start;
}
...
```

##### 4.2.7 `jump` #####

A `jump` statement has the following syntax:
```
conv jump addr_expr ( expr1, ..., exprN ) ;
``` 

This statement jumps to the address specified by `addr_expr`'s value and passes arguments `expr1`, ..., `exprN` according to the specified `conv` calling convention.

If there are no arguments, empty parentheses (`()`) should still be present.

`addr_expr`'s value will be **truncated** or **zero-extended** to the `ptr` type's actual size limit.

Each `exprI`'s types **must** be defined to match whatever the called function expects.  Casting can be used as necessary. Simple constants, such as characters and integer literals, are by default the widest available type and normally should be casted.

When executing a `jump` statement, the current function's stack frame (i.e. all of its registers) will be deleted.

If the number and types of arguments are different from what the called function expects, the resulting behaviour is undefined.

##### 4.2.8 Function Call #####

A function call has the following syntax:
```
conv ( type ) name = funct_expr ( expr1, ..., exprN ) ;
```

This statement calls the function specified by `addr_expr`'s value and passes arguments `expr1`, ..., `exprN` according to the specified `conv` calling convention.

If the called function does not return any value, `type`, `name` and the equal sign should be omitted.
```
conv ( ) funct_expr ( ... ) ;
```

The `name` and equal sign can also be omitted when `type` is present, in which case the return value will be ignored.

If present, `name` must be an existing register of the same type as `type`.

`funct_expr`'s value will be **truncated** or **zero-extended** to the `ptr` type's actual size limit.

Each `exprI` has the same restrictions as a `jump` statement.

However, unlike the `jump` statement, the current function's stack frame is not deleted. The called function will thus be allowed to return execution to the calling functions via the `return` statement.

Again, if the number and types of arguments or the type of return value are different from what the called function expects, the resulting behaviour is undefined.

##### 4.2.9 `return` #####

The `return` statement has the following syntax:
```
return expr ;
```

This statement returns control to the code that called the function.

`expr`'s value will be **truncated** or **zero-extended** to the function header's specified type. If the function has no return type, `expr` must omitted.

Upon returning, the called function's stack frame will be deleted.

##### 4.2.10 Block #####

A block is simply a list of statements within braces (`{}`). It offers no scoping but may be used for grouping code together.

## 5 Expressions ##

An expression can be a constant, a memory read, a cast, or an application of an operator on other expressions. It represents a value.

There is no real distinction between signed and unsigned numbers. It is instead the operators that make this distinction.

### 5.1 Memory Read ###

A memory read expression has the following syntax:
```
type [ addr_expr ]
```

`addr_expr`'s value will be **truncated** or **zero-extended** to the `ptr` type's actual size limit.

`addr_expr`'s value represents the address to read from, and `type` represents the type of data (and therefore how many words) to read.

This expression returns the value of type `type` at the specified memory address `addr_expr`

### 5.2 Casting ###

A cast expression has the following syntax:
```
type ( expr )
type $ ( expr )
```

If the size limit of `type` is smaller than the size limit of `expr`'s type, then both cast expressions will truncate `expr`'s value to fit within `type`.

If the size limit of `type` is greater than the size limit of `expr`'s type, then the extension behaviour depends on which expression is used:

1. `type ( expr )` will zero-extend the value, as it is the "unsigned cast".

2. `type $ ( expr )` will sign-extend the value, as it is the "signed cast".

This expression returns the truncated or extended value of type `type` corresponding to `expr`

### 5.3 Operators ###

Operators always take two expressions and executes an operation on both. If both sides of the expression have different types, the wider type of the two is selected.

| op  | Description         |
|-----|---------------------|
| +   | Addition            |
| -   | Substraction        |
| \*  | Multiplication      |
| /   | Unsigned division   |
| /$  | Signed division     |
| %   | Unsigned modulo     |
| /%  | Signd modulo        |
| &   | Bitwise AND         |
| \|  | Bitwise OR          |
| ^   | Bitwise XOR         |
| ~&  | Bitwise NAND        |
| ~\| | Bitwise NOR         |
| ~^  | Bitwise XNOR        |
| <<  | Left shift          |
| >>  | Logical right shift |
| >>$ | Arith. right shift  |

Operator precedence:
1. \* / /$ %
2. \+ \-      
3. << >> >>$
4. & ~&     
5. ^ ~^     
6. \| ~\|   
