from shexer.shaper import Shaper
from shexer.consts import TURTLE

in_list = [
"disease-disease",
"disease-group",
"disease-phenotype",
"doClass",
#"gda_score",
"gene",
"geneSymbol",
"hpoClass",
"meshClass",
"protein",
"proteinClass",
#"pubmed",
"umlsSTY",
#"variant",
"variant_frequencies",
#"vda",
#"vda_score",
"void-disgenet",
"void"
]
in_pattern = r"F:\datasets\disgenet\{}.ttl"
out_path = r"F:\datasets\disgenet\shapes.shex"

in_files = [in_pattern.format(a_str) for a_str in in_list]

shaper = Shaper(graph_list_of_files_input=in_files,
                all_classes_mode=True,
                input_format=TURTLE)

shaper.shex_graph(output_file=out_path,
                  verbose=True)

