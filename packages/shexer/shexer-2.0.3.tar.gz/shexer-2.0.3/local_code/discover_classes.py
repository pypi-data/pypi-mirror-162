from shexer.io.sparql.query import \
    query_endpoint_po_of_an_s, \
    query_endpoint_single_variable, \
    query_endpoint_sp_of_an_o

str_query = "SELECT distinct {0} where {{ {1} {2} {0} . }}".format("?o",
                                                           "?s",
                                                           "a")
print(str_query)
for an_elem in query_endpoint_single_variable(endpoint_url="https://agrovoc.fao.org/sparql",
                                              str_query=str_query,
                                              variable_id="o"):
    print(an_elem)
print("Done!")