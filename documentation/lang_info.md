# Solar Programming Language (SPL) #

## 1. Description ##

The Solar Programming Language (SPL) is a C-like, procedural, unsafe, statically and explicitly typed language.
It was designed initially for the homebrew Mercury instruction set with plans to be compilable for other homebrew CPUs.
SPL is simply an amateur experiment with compilation and a tool made to test simple homebrew CPUs.

This Git repository contains documentation on SPL as well as a compiler toolchain with a Mercury Assembly backend

## 2. Environment ##

Just like C, there are multiple environments/scopes that all keep track of their own variables and procedures.

A translation unit is a singular file after preprocessing.
The topmost (program) environment is the program environment, which keeps track of all the variables across all translation units.

Each translation unit has a global environment.
By default, all global symbols will be present in the program environment unless specified as `private`.
Procedure can only exist within the global environment of a translation unit.

Each procedure possesses its own procedure environment.

Finally, each compound statement possesses its own local environment.

Lower scopes have access to the symbols of higher scopes they have been declared in.

## 3. Language ##