#!/usr/bin/python3

import string, requests, re, subprocess, os,contextlib, urllib
from termcolor import colored
from bs4 import BeautifulSoup
import bibtexparser as parser

@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)

def getValue(dict, key, default):
    if key in dict:
        return dict[key].value
    else:
        return default

def getDoi():

    bibFile = ""
    for _, _, files in os.walk("./"):
        for file in files:
            if file.endswith(".bib"):
                bibFile = file
                break

        if bibFile != "":
            break

    if bibFile == "":
        return None
    
    library = parser.parse_file(bibFile)

    for entry in library.entries:
        fields = {k.lower(): v for k, v in entry.fields_dict.items()}
        doi = getValue(fields, 'doi', "").strip()

        if doi != "":
            doi = doi.removeprefix("https://dx.doi.org/")
            doi = doi.removeprefix("https://doi.org/")
            doi = doi.removeprefix("http://dx.doi.org/")
            doi = doi.removeprefix("http://doi.org/")

            return doi

    return None

def addPdf(pdfUrl, pdfFile):

    print(f"PDFURL {pdfUrl}")

    try:
        response = urllib.request.urlopen(pdfUrl)
        size = int(response.headers.get('content-length'))

        if size > 2_000_000:
            print(f"TOOLARGE {size}")
            open("addPdf.log", 'wb').write(b"PDF too large")
            return

        contents = response.read()

        # try to extract a pdf file name
        if pdfFile is None or pdfFile == "":
            headers = response.headers
            pdfFile = headers.get_filename()

        if pdfFile is None or pdfFile == "":
            path = urllib.parse.urlparse(response.url).path
            pdfFile = path[path.rfind('/') + 1:]

        if pdfFile is None or pdfFile == "":
            pdfFile = "article.pdf"

        open(pdfFile, 'wb').write(contents)

        print(f"GITADD {pdfFile}")
        subprocess.run(["git", "add", pdfFile])

    except Exception as e:
        print(f"EXCEPT {e}")

# url could be a doi url
def fetchPdf(url):

    # use sci-hub if we have a doi or url

    # http://dx.doi.org/10.1145/358746.358767
    # https://dx.doi.org/10.1145/358746.358767
    # https://www.sciencedirect.com/science/article/pii/S0304397500001006
    # https://sci-hub.se/10.1145/358746.358767

    sciHubRoot = "https://sci-hub.se/"
    sciHub = sciHubRoot + url
    print(f"SCIHUB URL {sciHub}")

    try:
        req = requests.get(sciHub, allow_redirects=True)
        html = req.content.decode("utf-8") 
        soup = BeautifulSoup(html, features="html.parser")
        pdfElement = soup.find(attrs={'id': 'pdf'})

        if pdfElement is not None:
            print(f"SCIHUB ELEMENT {pdfElement}")

            srcUrl = pdfElement['src']
            if srcUrl.startswith("//"):
                pdfUrl = "https:" + srcUrl
            else:
                pdfUrl = sciHubRoot + srcUrl

            addPdf(pdfUrl, "")

    except Exception as e:
        print(f"SCIHUB EXCEPT " + e)

for root, dirs, _ in os.walk("./entries"):

    n = len(dirs)
    yes = no = 0
    i = 0

    for dir in dirs:
        cwd = os.path.join(root, dir)
        i = i + 1
        with pushd(cwd):
            print(f"CWD {i}/{n} {os.getcwd()}")

            pdfFound = False

            for pdfFile in os.listdir("./"):
                if pdfFile.endswith(".pdf"):
                    pdfFound = True
                    print(colored("PDF FOUND", "green"))
                    yes += 1
                    break

            if pdfFound:
                continue

            print(colored("NO PDF", "red"))
            no += 1

            # this directory does not contain any pdf

            # get the doi from the bib
            doi = getDoi()

            if doi is None:
                print(colored("NO DOI", "red"))
                continue

            print(f"DOI {doi}")
            fetchPdf(doi)

    # only walk directly inside ./entries
    break

print(f"Summary: yes {yes}, no {no}")