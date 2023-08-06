from shexer.io.graph.yielder.big_ttl_triples_yielder import BigTtlTriplesYielder
from time import time

source_file = r"F:\datasets\wikidata\wikidata-20150518-all-BETA.ttl\wikidata-20150518-all-BETA.ttl"

yielder = BigTtlTriplesYielder(source_file=source_file,
                               allow_untyped_numbers=True)
counter = 0
ini = time()
print("Here I go!")
for a_triple in yielder.yield_triples():
    counter += 1
    if counter %100000 == 0:
        print(counter)
print("Done!")
print(counter)
print(time() - ini)

# import os.path as pth
#
#
# r = pth.join(pth.dirname(pth.normpath(__file__)), "t_files" + pth.sep)
# print(pth.sep)
# print(r)
# print(type(r))