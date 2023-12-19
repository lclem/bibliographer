#!/usr/bin/python3
import os, sys, contextlib, requests, re
from pypdf import PdfReader, PdfWriter, generic
from bs4 import BeautifulSoup
from selenium import webdriver

writeNewPdf = False

if len(sys.argv) > 1 and sys.argv[1] == "--writePdf":
    print("OPTION --writePdf")
    writeNewPdf = True

doisWeHave = set()
doisWeDontHave = set()
urisWeHave = set()
urisWeDontHave = set()
unresolvedUris = set()

def loadSetFromFile(fileName, set):
    try:
        with open(fileName, "r") as f:
            for line in f:
                set.add(line.strip())
    except:
        pass

doisCheckedFilename = "doisChecked.txt"
doisWeHaveFileName = "doisWeHave.txt"
doisWeDontHaveFileName = "doisWeDontHave.txt"
urisWeHaveFileName = "urisWeHave.txt"
urisWeDontHaveFileName = "urisWeDontHave.txt"

fileNamesSets = [
    ("doisWeHave.txt", doisWeHave),
    ("doisWeDontHave.txt", doisWeDontHave),
    ("urisWeHave.txt", urisWeHave),
    ("urisWeDontHave.txt", urisWeDontHave)]

for fileName, set in fileNamesSets:
    loadSetFromFile(fileName, set)

doisWeHaveFileName = "../../" + doisWeHaveFileName
doisWeDontHaveFileName = "../../" + doisWeDontHaveFileName
urisWeHaveFileName = "../../" + urisWeHaveFileName
urisWeDontHaveFileName = "../../" + urisWeDontHaveFileName

@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)

def remove_prefix(input_string, prefix):
    if prefix and input_string.startswith(prefix):
        return input_string[len(prefix):]
    return input_string

# https://www.sciencedirect.com/science/article/pii/S0304397507001582
# http://doi.acm.org/10.1145/322234.322243
# https://ora.ox.ac.uk/objects/uuid:f341421b-2130-42d7-bb21-52442bad0b80
# http://www.jstor.org/stable/1995086

def uri2doi(uri):

    # TODO: find DOIs of as many URIs as possible and return the DOI

    # https://arxiv.org/abs/2107.04455 --> https://doi.org/10.48550/arXiv.2107.04455
    if "arxiv.org" in uri:
        last = uri.split("/")[-1]
        if len(last) > 5 and last[-2] == "v":
            last = last.split("v")[0]
        print("ARXIV " + last)
        return "https://doi.org/10.48550/arXiv." + last
    
    # https://hal.inria.fr/inria-00072528
    # if "inria." in uri:
    
    # https://www.sciencedirect.com/science/article/pii/S0304397507001582
    if "sciencedirect.com" in uri:

        print("SCIENCEDIRECT " + uri)

        # req = requests.get(uri, allow_redirects=True)
        # html = req.content.decode("utf-8")

        driver = webdriver.Chrome() #executable_path=yourdriver)
        driver.get(uri)
        html = driver.page_source

        # print("html: " + html)

        soup = BeautifulSoup(html, features="html.parser")
        doiElement = soup.find(attrs={'class': 'doi'})

        # print("soup found doi element: ")
        # print(doiElement)

        if doiElement is not None:
            href = doiElement["href"]
            
            if href is not None:
                print(f"SCIENCEDIRECT DOI {href}")
                # input("Press Enter to continue...")

                return href
                
        print(f"SCIENCEDIRECT NO DOI")

    return uri

def isDOI(uri):
    return "doi.org" in uri

# TODO: 1) try to also rewrite non-doi URI to (our) doi URI
# TODO: 2) when this is not possible (because no doi exists or we are unable to find it),
# it would be nice to find a way to rewrite to the corresponding slug if we have it

def rewriteURI(uri):

    # print("rewriteURI: " + uri)

    doiURI = uri2doi(uri)
    if isDOI(doiURI):
        # we have successfully rewritten the URI to a DOI URI
        return rewriteDOI(uri, doiURI)
    
    # treat the non-DOI URI 
    uriStripped = uri
    uriStripped = remove_prefix(uriStripped, "https://")
    uriStripped = remove_prefix(uriStripped, "http://")
    
    newUri = f"https://lclem.github.io/bibliographer/articles/{uriStripped}"

    if uriStripped in urisWeDontHave:
        print("URI NO (cache hit)")
        return uri
    elif uriStripped in urisWeHave:
        print("URI YES (cache hit)")
        return newUri
    else:
        response = requests.get(newUri)

        if response.status_code == 200:
            print(f"URI YES {newUri}")
            urisWeHave.add(uriStripped)

            with open(urisWeHaveFileName, 'a') as f:
                f.write(f"{uriStripped}\n")

            return newUri
        else:
            print(f"URI NO {newUri}")
            urisWeDontHave.add(uriStripped)

            with open(urisWeDontHaveFileName, 'a') as f:
                f.write(f"{uriStripped}\n")

            return uri
        
def rewriteDOI(uri, doiURI):

    # https://doi.org/10.4230/LIPIcs.FSTTCS.2010.1
    parts = doiURI.split("/")

    if len(parts) < 2:
        return uri

    doi = ""
    doiPattern = "^10\.[0-9][0-9][0-9][0-9][0-9]*"
    for i, part in enumerate(parts):
        if re.search(doiPattern, part):
            leftoverParts = parts[i:]
            doi = "/".join(leftoverParts)
            break

    if doi == "":
        return uri
    
    # this assumes that the doi is the slug with which the article is published
    newUri = f"https://lclem.github.io/bibliographer/articles/{doi}"

    if doi in doisWeDontHave:
        print("DOI NO (cache hit)")
        return uri
    elif doi in doisWeHave:
        print("DOI YES (cache hit)")
        return newUri
    else:
        response = requests.get(newUri)

        if response.status_code == 200:
            print(f"DOI YES {newUri}")
            doisWeHave.add(doi)

            with open(doisWeHaveFileName, 'a') as f:
                f.write(f"{doi}\n")

            return newUri
        else:
            print(f"DOI NO {newUri}")
            doisWeDontHave.add(doi)

            with open(doisWeDontHaveFileName, 'a') as f:
                f.write(f"{doi}\n")

            return uri

def processPDF(pdfFile):

    print(f"PDF {pdfFile}")

    pdfChanged = False

    try:
        reader = PdfReader(pdfFile)
    except Exception as e:
        print(f"EXCEPTION {e}")
        return False

    for page in reader.pages:
        annotations = page.annotations

        if annotations is None:
            continue

        for annot in annotations:
            obj = annot.get_object()
            if "/A" in obj:
                A = obj["/A"]
                # print(A)
                # {'/S': '/GoTo', '/D': 'section*.18'}
                # {'/Type': '/Action', '/S': '/URI', '/URI': 'https://doi.org/10.4230/LIPIcs.FSTTCS.2010.1'}

                if "/URI" in A:
                    uri = A["/URI"]

                    if type(uri) is not str:
                        urienc = str(uri)
                        # print(f"ENC {uri} --> {urienc}")
                        uri = urienc

                    new_uri = rewriteURI(uri)

                    if uri == new_uri:
                        print(f"URI {uri}")
                    else:
                        print(f"URI {uri} --> {new_uri}")

                        key   = generic.TextStringObject("/URI")
                        value = generic.TextStringObject(new_uri)
                        obj['/A'][key] = value

                        pdfChanged = True

    if writeNewPdf and pdfChanged:
        print(f"NEW-PDF {pdfFile}")

        writer = PdfWriter()
    
        for page in reader.pages:
            writer.add_page(page)

        writer.write(pdfFile)
        writer.close()
    
    return True

for root, dirs, _ in os.walk("./entries"):

    n = len(dirs)
    i = 0

    for dir in dirs:
        cwd = os.path.join(root, dir)
        i = i + 1
        with pushd(cwd):
            print(f"\nCWD {i}/{n} | YES {len(doisWeHave)} NO {len(doisWeDontHave)} | {os.getcwd()}")

            if True or not os.path.exists(doisCheckedFilename):

                allGood = True
                somePdfProcessed = False

                for _, _, files in os.walk("./"):

                    for pdfFile in files:
                        if pdfFile.endswith(".pdf") and not pdfFile.startswith("._"):
                            res = processPDF(pdfFile)
                            allGood = allGood and res
                            somePdfProcessed = True

                if allGood and somePdfProcessed:
                    open(doisCheckedFilename, "w").close()

    # only walk directly inside ./entries
    break