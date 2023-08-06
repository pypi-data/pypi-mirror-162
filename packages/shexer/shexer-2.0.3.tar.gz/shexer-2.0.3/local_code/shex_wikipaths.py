import os
from shexer.shaper import Shaper
from shexer.consts import TURTLE

def run(base_input_dir,
        out_path,
        namespaces):

    in_files = [os.path.join(dp, f) for dp, dn, filenames in
                os.walk(base_input_dir) for f in filenames
                if os.path.splitext(f)[1] == '.ttl']

    shaper = Shaper(graph_list_of_files_input=in_files,
                    all_classes_mode=True,
                    input_format=TURTLE,
                    namespaces_dict=namespaces,
                    disable_exact_cardinality=True)

    # Verbose active mode, so one can check in which stage is the execution, some raw numbers
    # about shapes and instances computed, and also execution times

    # This acceptance_threshold filters any information observed in less than 5% of the
    # instances of any class.
    shaper.shex_graph(output_file=out_path,
                      verbose=True,
                      acceptance_threshold=0.05)

    print("Done!")

if __name__ == "__main__":
    ############### CONFIGURATION ###############

    # Directory with the wikipathways dump (content unzipped). the process will recursively look
    # for any ttl file in this folder or any of this subfolders, and it will merge it in a single
    # graph
    base_input_dir = r"F:\datasets\wikipathways"

    # output shex file
    out_path = r"F:\datasets\wikipathways\wikipathways_v2.shex"

    # namespace-prefix pair to be used in the results
    namespaces_dict = {"http://purl.org/dc/terms/": "dc",
                       "http://rdfs.org/ns/void#": "void",
                       "http://www.w3.org/2001/XMLSchema#": "xsd",
                       "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
                       "http://purl.org/pav/": "pav",
                       "http://www.w3.org/ns/dcat#": "dcat",
                       "http://xmlns.com/foaf/0.1/": "foaf",
                       "http://www.w3.org/2002/07/owl#": "owl",
                       "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
                       "http://www.w3.org/2004/02/skos/core#": "skos",
                       "http://vocabularies.wikipathways.org/gpml#": "gpml",
                       }
    ############### EXECUTION ###############

    run(base_input_dir=base_input_dir,
        out_path=out_path,
        namespaces=namespaces_dict)
