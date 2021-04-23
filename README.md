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

that function will return the content of a docassemble interview that should function
on a server with this module and scasp installed, such as the [l4-docassemble server](https://github.com/smucclaw/l4-docassemble).

It also includes a specialized version of the docassemble-datatypes generic questions, called l4.yml,
which is included automatically in interviews created with `generate_interview`.