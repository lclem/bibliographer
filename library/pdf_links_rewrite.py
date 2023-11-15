#!/usr/bin/python3
import os, sys, contextlib, requests, re
from pypdf import PdfReader, PdfWriter, generic

writeNewPdf = False

if len(sys.argv) > 1 and sys.argv[1] == "--writePdf":
    writeNewPdf = True

doisWeHave = set()
doisWeDontHave = set()
unresolvedUris = set()

doisCheckedFilename = "doisChecked.txt"
doisWeHaveFileName = "doisWeHave.txt"
doisWeDontHaveFileName = "doisWeDontHave.txt"

try:
    with open(doisWeHaveFileName, "r") as f:
        for line in f:
            doi = line.strip()
            print(f"DOI YES {doi}")
            doisWeHave.add(doi)
except:
    pass

try:
    with open(doisWeDontHaveFileName, "r") as f:
        for line in f:
            doi = line.strip()
            print(f"DOI NO {doi}")
            doisWeDontHave.add(doi)
except:
    pass

# open(doisWeDontHaveFileName, 'w').close()

doisWeDontHaveFileName = "../../" + doisWeDontHaveFileName
doisWeHaveFileName = "../../" + doisWeHaveFileName

@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)

# https://www.sciencedirect.com/science/article/pii/S0304397507001582
# http://doi.acm.org/10.1145/322234.322243
# https://ora.ox.ac.uk/objects/uuid:f341421b-2130-42d7-bb21-52442bad0b80
# http://www.jstor.org/stable/1995086

def uri2doi(uri):
    return uri

def isDOI(uri):
    # print(f"isDOI {uri}, type = {type(uri)}")

    # if type(uri) is bytes:
    #     return False

    return "doi.org" in uri

def rewriteURI(uri):

    # if type(uri) is bytes:
    #     return uri

    doiUri = uri2doi(uri)

    if not isDOI(doiUri):
        return uri

    # https://doi.org/10.4230/LIPIcs.FSTTCS.2010.1
    parts = doiUri.split("/")

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
                        print(f"ENC {uri} --> {urienc}")
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

            if not os.path.exists(doisCheckedFilename):

                allGood = True
		somePdfProcessed = False

                for _, _, files in os.walk("./"):

                    for pdfFile in files:
                        if pdfFile.endswith(".pdf"):
                            res = processPDF(pdfFile)
                            allGood = allGood and res
			    somePdfProcessed = True

                if allGood and somePdfProcessed:
                    open(doisCheckedFilename, "w").close()

    # only walk directly inside ./entries
    break
