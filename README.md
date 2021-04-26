# docassemble-l4

This is a package that extends docassemble-scasp and docassemble-datatypes
to facilitate the rapid prototyping of expert systems based on code written
in the l4 language.

## Installation

Install this package using docassemble's package manager from the github source.

## Dependencies

* docassemble-scasp
* pyparsing
* networkx

## Use

The docassemble.l4.intgen namespace includes `generate_interview(LExSIS_source,scasp_source)`,
which accepts the contents of a LExSIS file as a string, and the contents of an s(CASP) source
file as a string. The scasp_source file contents are expected to use our LPDAT implementation
in s(CASP).

That function will return the content of a docassemble interview that should function
on a server with this module and scasp installed, such as the [l4-docassemble server](https://github.com/smucclaw/l4-docassemble).

You can also access that functionality in a friendlier interface by running the docassemble.l4:intgen.yml interview,
which accepts a LExSIS file and an s(CASP) file from the current user's playground static folder.