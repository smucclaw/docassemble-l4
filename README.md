# docassemble-l4

This is a package that extends docassemble-scasp and docassemble-datatypes
to facilitate the rapid prototyping of expert systems based on code written
in the l4 language.

## Installation

Install this package using docassemble's package manager from the github source.

## Dependencies

* docassemble-scasp
* gf-python
* pyparsing
* networkx

## Configuration

In order for the interview generator to be able to install newly-generated interviews onto your playground,
it needs API access. To provide that, go to "Profile", "Other Settings", "API Keys", and generate an API Key.
Then add it to your docassemble server configuration as follows:

```
l4:
  API Key: XXXXXXX
```

## Use

The docassemble.l4.intgen namespace includes `generate_interview(LExSIS_source,scasp_source)`,
which accepts the contents of a LExSIS file as a string, and the contents of an s(CASP) source
file as a string. The scasp_source file contents are expected to use our LPDAT implementation
in s(CASP).

That function will return the content of a docassemble interview that should function
on a server with this module and scasp installed, such as the [l4-docassemble server](https://github.com/smucclaw/l4-docassemble).

You can also access that functionality in a friendlier interface by running the docassemble.l4:intgen.yml interview,
which accepts a LExSIS file and an s(CASP) file from the current user's playground static folder.


#### Drafting interview generator files:  
- [s(CASP) example files](https://gitlab.software.imdea.org/ciao-lang/sCASP/-/tree/master/examples)
- [LExSIS Documentation](https://github.com/smucclaw/complaw/blob/primary/Publications/Documentation/LExSIS_Documentation.md)

It should be noted that drafting an s(CASP) file to be used for the interview generator is slightly different. Particularly, one does not include a model-finding query within the s(CASP) file, but instead adds it to the LExSIS file under the `query` header-value pair instead. For an example, see the treatment of a "Rock Paper Scissors" scenario from a [pure s(CASP)](https://medium.com/computational-law-diary/how-rules-as-code-makes-laws-better-115ab62ab6c4) perspective vs the [interview generation](https://github.com/smucclaw/docassemble-l4/blob/main/docassemble/l4/data/static/rps.pl) perspective.   

## Contributing
#### What should I read to understand what's happening?
If you've never used [docassemble](https://docassemble.org/docs/helloworld.html) before, we highly suggest that you familiarize yourself with it before proceeding.

Once you've got an idea of what docassemble does & how it works, we recommend you read the following articles:
  - [Docassemble package management](https://docassemble.org/docs/packages.html)
  - [DAObject](https://docassemble.org/docs/objects.html#DAObject)
  - [Generic Objects in docassemble](https://docassemble.org/docs/modifiers.html#generic%20object) 

After reading the above, familiarize yourself with the package. 
  - the bulk of the logic is located in [intgen.py](https://github.com/smucclaw/docassemble-l4/blob/main/docassemble/l4/intgen.py)
  - the user-facing interview generator is in [intgen.yml](https://github.com/smucclaw/docassemble-l4/blob/main/docassemble/l4/data/questions/intgen.yml)
  - the question defaults for the various datatypes used [l4.yml](https://github.com/smucclaw/docassemble-l4/blob/main/docassemble/l4/data/questions/l4.yml)

#### Developer Workflow
We use [pipenv](https://pipenv.pypa.io/en/latest/) to manage dependencies, and [pytest](https://docs.pytest.org/) to handle tests. 



