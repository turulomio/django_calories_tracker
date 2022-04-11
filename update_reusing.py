from argparse import ArgumentParser
from moneymoney.reusing.github import download_from_github
from os import remove

def replace_in_file(filename, s, r):
    data=open(filename,"r").read()
    remove(filename)
    data=data.replace(s,r)
    f=open(filename, "w")
    f.write(data)
    f.close()

parser=ArgumentParser()
parser.add_argument('--local', help='Parses files without download', action="store_true", default=False)
args=parser.parse_args()      

if args.local==False:
    download_from_github("turulomio", "reusingcode", "python/github.py", "moneymoney/reusing")
    download_from_github("turulomio", "reusingcode", "python/datetime_functions.py", "moneymoney/reusing")
    download_from_github("turulomio", "reusingcode", "python/text_inputs.py", "moneymoney/reusing")

