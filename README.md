# javascriptvoc
An RDF-based vocabulary to model Javascript into RDF. Javascript logic can thus be represented, queried, generated, validated, analysed, transformed and reused as semantic objects themselves.

# Abstract

The Javascript Vocabulary provides a formal representation of the Javascript programming language, enabling the modeling and generation of Javascript code through an abstract syntax tree (AST) framework. It defines classes and properties to describe the various components of Javascript syntax, including functions, classes, statements, expressions, and data structures. Additionally, it incorporates SHACL shapes for validating Javascript code structures and supports algorithms for serializing Javascript code from RDF representations. This vocabulary enhances code generation and manipulation, bridging Javascript with broader semantic web technologies.

# Description

The Javascript Vocabulary formalizes the Javascript programming language, offering a structured representation of its syntax and semantics. It defines classes for different Javascript constructs, such as 'js:Statement' for statements, 'js:Function' for functions, and properties to capture relationships between these components. Central to this vocabulary is the class 'js:Node', which serves as a building block for all types of Javascript code segments. Each code unit can have attributes, such as 'js:operator' for operators within expressions and 'js:argument' for defining parameters. The vocabulary also includes SHACL shapes to validate the correctness of Javascript code structures, ensuring that generated code adheres to Javascript syntax rules. These shapes facilitate the creation of well-formed Javascript code that can be executed reliably. This comprehensive approach allows users to leverage RDF representations to generate Javascript code, enabling seamless integration of semantic technologies with programming tasks.
    
The Javascript Core Vocabulary models the Javascript language based on its Abstract Syntax Tree (AST), as described in [EStree](https://github.com/estree/estree). 

# Objective

To tackle the challenges of Javascript code generation, maintenance, reuse and validation, we present the Javascript Vocabulary - a transformative framework designed to support users in managing Javascript programming. This vocabulary enables users to (1) model and represent Javascript code constructs, (2) generate and validate Javascript code programmatically, and (3) ensure adherence to Javascript syntax and best practices. By leveraging the power of RDF and the flexibility of an abstract syntax tree, the Javascript Vocabulary enhances the efficiency and reliability of code generation in programming environments, fostering better coding practices and facilitating collaboration in software development projects.

# Audience

This document is intended for a diverse audience of software developers, data scientists, educators, and anyone involved in Javascript programming and code management. It aims to support users seeking to enhance their understanding and application of Javascript within the context of semantic technologies and code generation.

# Status

Unstable & unfinished. Work in progress. Please note that the provided tooling in this repo is dependent on RDFlib, which at the moment contains a bug that prevents the code from running. See [issue 2957](https://github.com/RDFLib/rdflib/issues/2957). It is advised to use another triple store and SHACL engine for the moment.

# Example - Hello World!

Take for example the following Javascript code:

```
console.log("Hello world!")
```

This can be modeled in RDF using the Javascript Vocabulary:

```
prefix ex:  <https://example.org/>
prefix js:  <https://www.javascript.fin.rijksweb/model/def/>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

# Root node of the AST (Program node)
ex:program1
  a js:Program ;
  js:body (ex:expressionStatement1) ;
  js:fragment '''console.log("Hello world!");'''.  

# ExpressionStatement
ex:expressionStatement1
  a js:ExpressionStatement ;
  js:expression ex:callExpression1;
  js:fragment '''console.log("Hello world!");'''.

# CallExpression node
ex:callExpression1
  a js:CallExpression ;
  js:callee    ex:memberExpression1 ;
  js:arguments (ex:argument1) ;
  js:fragment '''console.log("Hello world!")'''.  

# MemberExpression node
ex:memberExpression1
  a js:MemberExpression ;
  js:object   ex:identifierConsole ;
  js:property ex:identifierLog ;
  js:computed false;
  js:fragment '''console.log'''.

# Identifier object 'console'
ex:identifierConsole
  a js:Identifier ;
  js:name '''console''' ;
  js:fragment '''console'''.  

# Identifier property 'log'
ex:identifierLog
  a js:Identifier ;
  js:name '''log''';
  js:fragment '''log'''.

# Literal
ex:argument1
  a js:Literal ;
  js:value '''Hello world!''' ;
  js:raw '''\"hello world!\"''';
  js:fragment '''"Hello world!"'''.   

``` 
 