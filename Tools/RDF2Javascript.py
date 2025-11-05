# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 18:40:53 2023

@author: Flores Bakker

The RDF2Javascript script to serialize RDF-based model of arbitrary Javascript based Abstract Syntax Trees into actual javascript code.

Usage: 

1. Place an arbitrary RDF-based Abstract Syntax Tree snippet of Javascript (as trig file *.trig) in the input folder.
2. In the command prompt, run 'python RDF2Javascript.py'
3. Go to the output folder and grab your enriched trig file, now including Javascript fragments.


"""
import os
import pyshacl
import rdflib 
from rdflib import Namespace, Dataset

# Get the current working directory in which the RDF2Javascript.py file is located.
current_dir = os.getcwd()

# Set the path to the desired standard directory. 
directory_path = os.path.abspath(os.path.join(current_dir))

# namespace declaration
js = Namespace("https://www.javascript.fin.rijksweb/model/def/")

# Function to read a graph (as a string) from a file 
def readGraphFromFile(file_path):
    # Open each file in read mode
    with open(file_path, 'r', encoding='utf-8') as file:
            # Read the content of the file and append it to the existing string
            file_content = file.read()
    return file_content

# Function to write a graph to a file
def writeGraph(graph):
    graph.serialize(destination=directory_path+"/Tools/Output/"+filename_stem+"-javascript.trig", format="trig")

# Function to call the PyShacl engine so that a RDF model of an Javascript script can be serialized to Javascript code.
def iteratePyShacl(javascript_generator, serializable_graph):
        
        # call PyShacl engine and apply the Javascript vocabulary to the serializable Javascript model
        pyshacl.validate(
        data_graph=serializable_graph,
        shacl_graph=javascript_generator,
        data_graph_format="trig",
        shacl_graph_format="trig",
        advanced=True,
        inplace=True,
        inference=None,
        iterate_rules=False, #rather than setting this to true, it is better to do the iteration in the script as PyShacl seems to have some buggy behavior around iteration.
        debug=False,
        )
        
       
        statusquery = serializable_graph.query('''
            
prefix js:  <https://www.javascript.fin.rijksweb.nl/model/def/>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

ASK
WHERE 
  {
  ?script 
        rdf:type js:Program;
        js:fragment [].
}
        ''')   

        resultquery = serializable_graph.query('''
            
prefix js:  <https://www.javascript.fin.rijksweb.nl/model/def/>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?javascriptFragment
WHERE {
  ?script 
         rdf:type js:Program;
         js:fragment ?javascriptFragment.
  
}

        ''')   

        # Check whether another iteration is needed. If the AST program node contains a javascript:syntax statement, the processing is considered done.
        for status in statusquery:
            print ('status = ', status)
            if status == False:
                writeGraph(serializable_graph)
                iteratePyShacl(javascript_generator, serializable_graph)
            else: 
                 print ("File " + filename_stem+"-javascript.trig" + " created in output folder.")
                 writeGraph(serializable_graph)
        
                 for result in resultquery:
                    javascript_fragment = result["javascriptFragment"]
                    output_file_path = directory_path+"/Tools/Output/"+filename_stem+".js"
                    
                    # Write the javascript content to the output file
                    with open(output_file_path, "w", encoding="utf-8") as file:
                        file.write(javascript_fragment)
                    print ("File " + filename_stem+".rq" + " created in output folder.")

                 
# loop through any turtle files in the input directory
for filename in os.listdir(directory_path+"/Tools/Input"):
    if filename.endswith(".trig"):
        file_path = os.path.join(directory_path+"/Tools/Input", filename)
        
        # Establish the stem of the file name for reuse in newly created files
        filename_stem = os.path.splitext(filename)[0]
        
        # Get the Javascript vocabulary and place it in a string
        javascript_generator = readGraphFromFile(directory_path+"/Specification/javascriptvoc - core.trig")
        
        # Get some Javascript code represented in triples
        javascript_script_string = readGraphFromFile(file_path) + '\n' + '\n' +  javascript_generator + '\n'
        
        # Create a graph
        serializable_graph = Dataset(default_union=True)
        serializable_graph.parse(data=javascript_script_string , format="trig")
        serializable_graph.bind("js", js)
                        
        # Inform user
        print ('\nCreating javascript fragments for file',filename, '...')
        
        # Call the shacl engine with the Javascript vocabulary
        iteratePyShacl(javascript_generator, serializable_graph)
        
        # Inform user
        print ('Done.')
