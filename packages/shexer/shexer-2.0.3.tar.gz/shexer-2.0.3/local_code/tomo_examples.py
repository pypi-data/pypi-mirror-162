from shexer.shaper import Shaper

########################### QUALIFIER SHAPES

namespaces_to_ignore = [
                        "http://www.wikidata.org/prop/direct",
                        "http://www.wikidata.org/prop/direct-normalized/"
                       ]

shaper = Shaper(target_classes=["http://www.wikidata.org/entity/Q85795487"],
                url_endpoint="https://query.wikidata.org/sparql",
                instantiation_property="http://www.wikidata.org/prop/direct/P31",
                namespaces_to_ignore=namespaces_to_ignore,
                wikidata_annotation=True,
                depth_for_building_subgraph=2,
                shape_qualifiers_mode=True,
                namespaces_for_qualifier_props=["http://www.wikidata.org/prop/"])

print(shaper.shex_graph(string_output=True))



########################## wikidata direct properties

namespaces_to_ignore = ["http://www.wikidata.org/prop/",
                        "http://www.w3.org/2004/02/skos/core#",
                        "http://schema.org/",
                        "http://wikiba.se/ontology#",
                        "http://www.wikidata.org/prop/direct-normalized/"]

shaper = Shaper(target_classes=["http://www.wikidata.org/entity/Q85795487"],
                url_endpoint="https://query.wikidata.org/sparql",
                instantiation_property="http://www.wikidata.org/prop/direct/P31",
                namespaces_to_ignore=namespaces_to_ignore)

print(shaper.shex_graph(string_output=True))


################################## DISABLE EXACT

shaper = Shaper(all_classes_mode=True,
                graph_file_input="/path/local_file.nt",
                disable_exact_cardinality=True)

print(shaper.shex_graph(string_output=True))

################################### EMPTY SHAPES

shaper = Shaper(all_classes_mode=True,
                graph_file_input="/path/local_file.nt",
                remove_empty_shapes=False)

print(shaper.shex_graph(string_output=True))


###################################  ALL COMPLIANT


shaper = Shaper(all_classes_mode=True,
                graph_file_input="/path/local_file.nt",
                all_instances_are_compliant_mode=False)

print(shaper.shex_graph(string_output=True))

################################### INVERSE PATHS

shaper = Shaper(all_classes_mode=True,
                graph_file_input="/path/local_file.nt",
                inverse_paths=True)

print(shaper.shex_graph(string_output=True))

##################################  THRESHOLD

shaper = Shaper(all_classes_mode=True,
                graph_file_input="/path/local_file.nt")

# The acceptance_threshold should always be a value
# in the range [0,1]. the default configuration is 0
print(shaper.shex_graph(string_output=True,
                        acceptance_threshold=0.3))

############################# SHACL
from shexer.consts import SHACL_TURTLE

shaper = Shaper(all_classes_mode=True,
                graph_file_input="/path/local_file.nt")

# output_format also accepts the value const.ShExC
# const.ShExC is the value used by default
print(shaper.shex_graph(string_output=True,
                        output_format=SHACL_TURTLE))


############################ NAMESPACES

namespaces = {"http://example.org/" : "ex",
               "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
               "http://www.w3.org/2001/XMLSchema#": "xsd"
            }

shaper = Shaper(all_classes_mode=True,
                namespaces_dict=namespaces,
                graph_file_input="/path/local_file.nt")

print(shaper.shex_graph(string_output=True))

###############################  several targets

shaper = Shaper(url_endpoint="https://example.org/sparql",
                depth_for_building_subgraph=2,
                shape_map_raw="<http://example.org/Jimmy>@<Person>",
                all_classes_mode=True)

print(shaper.shex_graph(string_output=True))


################################# ENDPOINT

# The default value for depth_for_building_subgraph is 1,
# so there is no need to set this parameter in case the
# user does not want to explore deeper regions of the
# graph
shaper = Shaper(url_endpoint="https://example.org/sparql",
                track_classes_for_entities_at_last_depth_level=True,
                all_classes_mode=True)

print(shaper.shex_graph(string_output=True))


#################################################### Intro
local_graph = "/disk/path/to/local/ntriples_file.nt"

shaper = Shaper(all_classes_mode=True,
                graph_file_input=local_graph)

res = shaper.shex_graph(string_output=True)
print(res)