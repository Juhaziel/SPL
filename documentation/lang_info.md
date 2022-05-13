# Solar Programming Language (SPL) #

## 1. Description ##

The Solar Programming Language (SPL) is a C-like, procedural, unsafe, statically and explicitly typed language.
It was designed initially for the homebrew Mercury instruction set with plans to be compilable for other homebrew CPUs.
SPL is simply an amateur experiment with compilation and a tool made to test simple homebrew CPUs.

This Git repository contains documentation on SPL as well as a compiler toolchain with a Mercury Assembly backend

## 2. Language ##

### 2.1 Concepts ###

#### 2.1.1 Namespaces ####
A namespace is a set of unique identifiers.
Just like C, there are 4 namespaces:

	- Labels (loop names)
	- Tags (names of structures, enums and unions)
	- Members of structs and unions (each struct/union has its own namespace)
	- Everything else

#### 2.1.2 Scopes ####
A singular program can be divided into multiple scopes that each maintain their own set of identifiers.


#### 2.1.3 Types ####
