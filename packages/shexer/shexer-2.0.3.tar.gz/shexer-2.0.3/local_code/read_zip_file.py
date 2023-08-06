from zipfile import ZipFile
import gzip

path = r"C:\Users\Dani\repos-git\shexer\test\t_files\t_graph_1.zip"
path_gz = r"C:\Users\Dani\repos-git\shexer\test\t_files\t_graph_1.gz"

with ZipFile(path, 'r') as zip:
    with zip.open("t_graph_1.ttl") as in_file:
        for a_line in in_file:
            pass
            # print(a_line.decode("utf-8"))


    # for file in zip.namelist():
    #     print(file)

# archive = ZipFile(path, "r")
# data = archive.read("t_graph_1.ttl")


print("Done!")
with gzip.open(path_gz, "r") as in_file:
    for a_line in in_file:
        print(a_line.decode("utf-8"))

print("Done2!")