#!/usr/bin/python3

import glob, os
import contextlib
import bibtexparser as parser
import string
import urllib.parse
import requests
import subprocess
import re
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import urllib

@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)

substitutions = {
    r"\\relax\s*": "",
    r"\\`\s*a": "à",
    r"\\'\s*a": "á",
    r"\\'\s*A": "Á",
    r"\\=\s*a": "ā",
    r"(\\~|\\\\textasciitilde)\s*a": "ã",
    r"\\u\s*a": "ă",
    r'\\"\s*a': "ä",
    r'\\"\s*A': "Ä",
    r"\\\^\s*a": "â",
    r"\\u\s*a": "ă",
    r'\\k\s*a': "ą",
    r'\\c\s*a': "ą",
    r'\\aa': "å",
    r'\\ae': "æ",
    r'\\AE': "Æ",
    r"\\ss": "ß",
    r"\\v\s*c": "č",
    r"\\v\s*C": "Č",
    r"\\'\s*c": "ć",
    r"\\'\s*C": "Ć",
    r"\\c\s*c": "ç",
    r"\\c\s*C": "Ç",
    r"\\dj": "đ",
    r"\\DJ": "Đ",
    r"\\'\s*e": "é",
    r"\\'\s*E": "É",
    r"\\`\s*e": "è",
    r"\\\^\s*e": "",
    r"\\k\s*e": "ę",
    r"\\c\s*e": "ȩ",
    r'\\"\s*e': "ë",
    r"\\v\s*e": "ě",
    r"\\u\s*g": "ğ",
    r"\\'\s*(\\)?i": "í",
    r"\\\^\s*(\\)?i": "î",
    r'\\"\s*(\\)?i': "ï",
    r"\\'\s*I": "Í",
    r"\\l": "ł",
    r"\\L": "Ł",
    r'\\"\s*o': "ö",
    r'\\"\s*O': "Ö",
    r"\\'\s*o": "ó",
    r"\\'\s*O": "Ó",
    r"\\\^\s*o": "ô",
    r"\\H\s*o": "ő",
    r"(\\~|\\\\textasciitilde)\s*o": "õ",
    r"(\\~|\\\\textasciitilde)\s*O": "Õ",
    r"\\o": "ø",
    r'\\oe': "œ",
    r'\\OE': "Œ",
    r"(\\~|\\\\textasciitilde)\s*n": "ñ",
    r"\\'\s*n": "ń",
    r"\\v\s*n": "ň",
    r"\\v\s*r": "ř",
    r"\\v\s*R": "Ř",
    r"\\'\s*s": "ś",
    r"\\'\s*S": "Ś",
    r"\\v\s*s": "š",
    r"\\v\s*S": "Š",
    r"\\c\s*s": "ş",
    r"\\c\s*S": "Ş",
    r"\\c\s*t": "ţ",
    r"\\c\s*T": "Ţ",
    r'\\"\s*u': "ü",
    r'\\"\s*U': "Ü",
    r"\\`\s*u": "ù",
    r"\\'\s*u": "ú",
    r"(\\~|\\\\textasciitilde)\s*u": "ũ",
    r"\\r\s*u": "ů",
    r"\\\^\s*u": "û",
    r"\\'\s*y": "ý",
    r"\\.\s*z": "ż",
    r"\\v\s*z": "ž",
    r"\\v\s*Z": "Ž"
}

valid_characters = string.ascii_letters + string.digits + string.whitespace + '&+-<>*=^~`-,;:\'"./\\()[]ễ' + "".join(substitutions.values())

def remove_prefix(input_string, prefix):
    if prefix and input_string.startswith(prefix):
        return input_string[len(prefix):]
    return input_string

def sanitise(str):
    result = "".join(c for c in str if c in valid_characters)
    return result.encode('utf-8').decode("utf-8", "ignore")

def normalise_names_order(author):
    names = author.split(", ")
    names = names[1:] + [names[0]]
    names = " ".join(names)

    return names

def normalise(str):

    # orig = str
    str = re.sub(r"\s+", " ", str)
    str = sanitise(str)

    for key, value in substitutions.items():
        # str = str.replace(key, value)
        str = re.sub(key, value, str)

    # print(f"normalise {orig} => {str}\n")
    return str

def getValue(dict, key, default):
    if key in dict:
        return dict[key].value.strip()
    else:
        return default

def writeBib(entry, bibFile):
    library = parser.Library([entry])
    parser.write_file(bibFile, library)
    print(f"GITADD {bibFile}")
    subprocess.run(["git", "add", bibFile])

def parsebib(bibFile):
    library = parser.parse_file(bibFile)

    # print(f"Parsed {len(library.blocks)} blocks, including:"
    #     f"\n\t{len(library.entries)} entries"
    #     f"\n\t{len(library.comments)} comments"
    #     f"\n\t{len(library.strings)} strings and"
    #     f"\n\t{len(library.preambles)} preambles")

    # Comments have just one specific attribute
    # first_comment = library.comments[0]
    # first_comment.comment # The comment string

    result = []
    for entry in library.entries:
        fields = entry.fields_dict

        # print(f"FIELDS: {fields}")
        # print(f"key {entry.key}, type {entry.entry_type}, fields {entry.fields_dict} \n")

        key = entry.key
        key = key.encode('utf-8').decode("ascii", "ignore")
        
        fields =  {k.lower(): v for k, v in fields.items()}

        title = getValue(fields, "title", "N/A")
        title = normalise(title)

        year = getValue(fields, "year", "0")

        author = getValue(fields, "author", "N/A")
        author = normalise(author)
        authors = author.split(" and ")

        for i in range(0, len(authors)):
            authors[i] = normalise_names_order(authors[i])

# quantum-physics-quant-ph-15a69-20d15-representation-theory-mathrt-algebraic-geometry-mathag-fos-mathematics-fos-computer-17b99-fos-physical-sciences-68q15-information-sciences-16s50-15a72-68q25-15a21-16g99-17a40-15a63-20f40-computational-complexity-cscc-16g60-16z05-17a42-group-theory-mathgr-f13§

# computational-complexity_finite-variable-logics_equivalence_polynomial-time_finite-structures_first-order-logic_graph-isomorphism-problem_complexity-theoretic-difficulties_quantifier-free-reductions_completeness-result_counting-quantifiers_logic_polynomia

        keywordsOrig = getValue(fields, "keywords", "")
        keywords = set()
        for keyword in keywordsOrig.replace(", ", " and ").replace("; ", " and ").split(" and "):
            # cut long keywords
            keywordToAdd = keyword.strip()

            if len(keywordToAdd) >= 250:
                keywordToAdd = keywordToAdd[:250]

            # never include a semicolon in a keyword, it will interpreted as the keyword separator
            keywordToAdd = keywordToAdd.replace(";", "_")

            if len(keywordToAdd) > 0:
                keywords.add(keywordToAdd)

        date_added = getValue(fields, 'date-added', "")
        date_modified = getValue(fields, 'date-modified', "")

        url = getValue(fields, 'url', "")
        doi = getValue(fields, 'doi', "")

        if doi != "" and not doi.startswith("http"):
            doi = mkDoiUrl(doi)

        eprint = getValue(fields, 'eprint', "")
        journal = getValue(fields, 'journal', "")
        booktitle = getValue(fields, 'booktitle', "")

        result.append((entry, key, authors, title, year, date_added, date_modified, doi, url, eprint, journal, booktitle, keywords))

    # print(f"RES: {result}")
    return result

def addPDF(pdfUrl, pdfFile, pdfFiles):

    print(f"PDFURL {pdfUrl}")

    try:
        # response = requests.get(pdfUrl, allow_redirects=True)
        # disp = response.headers.keys()
        # print(f"RESPONSE {disp}")

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

        pdfFileEncoded = os.path.join(cwd, pdfFile)
        pdfFiles.append(pdfFileEncoded)

    except Exception as e:
        print(f"EXCEPT {e}")

def mkDoiUrl(doi):
    return f"https://dx.doi.org/{doi}"

def amendDOI(doi, eprint, journal, key):

    if not doi == "":
        return doi, False

    if not eprint == "" and "arXiv" in journal:
        absUrl = f"https://arxiv.org/abs/{eprint}"
        print(f"ARXIV-ABS {absUrl}")

        req = requests.get(absUrl, allow_redirects=True)
        html = req.content.decode("utf-8") 
        soup = BeautifulSoup(html, features="html.parser")
        doiElement = soup.find(attrs={'class': 'arxivdoi'})

        if doiElement is not None:
            doiA = doiElement.find("a")

            if doiA is not None:
                doi = doiA["href"]
                print(f"ARXIV-DOI {doi}")

                if doi is not None:
                    return doi, True

    # sometimes the citation key is the DOI
    # All DOI numbers begin with a 10 and contain a prefix and a suffix separated by a slash.
    # The prefix is a unique number of four or more digits assigned to organizations;
    # the suffix is assigned by the publisher and was designed to be flexible with publisher identification standards.
    # 10.1093/ajae/aaq063
    # 10.1371/journal.pgen.1001111

    doiPattern = "^10\.[0-9][0-9][0-9][0-9][0-9]*/.+"
    if re.search(doiPattern, key):

        doi = mkDoiUrl(key)
        response = requests.get(doi)

        if response.status_code == 200:
            print(f"KEY-DOI {doi}")
            return doi, True

    return doi, False

allAuthors = set()
allKeywords = set()
allKeys = set()

for root, dirs, files in os.walk("./library/entries"):
    i = 0
    errors = 0
    for dir in dirs:
        cwd = os.path.join(root, dir)
        with pushd(cwd):
            print(f"CWD {os.getcwd()}")
            for _, _, files in os.walk("./"):
                for file in files:
                    if file.endswith(".bib"):
                        bibFile = file # os.path.join(root, file)
                        # print(f"FILE {bibFile}")

                        text_file = open(bibFile, "r")
                        bibcontent = text_file.read().strip()
                        text_file.close()

                        biblines = bibcontent.split("\n")
                        for j in range(0, len(biblines)):
                            biblines[j] = "    " + biblines[j]

                        bibcontent = "\n".join(biblines)
                        
                        parseResults = parsebib(bibFile)

                        if parseResults == []:
                            errors = errors + 1

                        for bibEntry in parseResults:

                            entry, key, authors, title, year, date_added, date_modified, doi, url, eprint, journal, booktitle, keywords = bibEntry
                            print(f"BIB {authors} - {title}")

                            allAuthors.update(authors)
                            allKeys.add(key)
                            allKeywords.update(keywords)

                            doi, modified = amendDOI(doi, eprint, journal, key)

                            if modified:
                                print(f"NEW-DOI {doi}")
                                entry.set_field(parser.model.Field("doi", doi))
                                writeBib(entry, bibFile)

                            doiNoURL = doi

                            if doiNoURL != "":
                                doiNoURL = remove_prefix(doiNoURL, "https://dx.doi.org/")
                                doiNoURL = remove_prefix(doiNoURL, "https://doi.org/")
                                doiNoURL = remove_prefix(doiNoURL, "http://dx.doi.org/")
                                doiNoURL = remove_prefix(doiNoURL, "http://doi.org/")

                            strippedUrl = url
                            if strippedUrl != "":
                                strippedUrl = remove_prefix(strippedUrl, "https://")
                                strippedUrl = remove_prefix(strippedUrl, "http://")

                            pdfFiles = []
                            for pdfFile in os.listdir("./"):
                                if pdfFile.endswith(".pdf"):
                                    print(f"PDF {pdfFile}")
                                    pdfFileEncoded = os.path.join(cwd, pdfFile)
                                    # pdfFileEncoded = urllib.parse.quote(pdfFileEncoded)
                                    pdfFiles.append(pdfFileEncoded)

                            # if there is no PDF for an arxiv paper, get a pdf
                            if len(pdfFiles) == 0 and not eprint == "" and "arXiv" in journal:
                                pdfFile = f"{eprint}.pdf"
                                pdfUrl = f"https://arxiv.org/pdf/{pdfFile}"
                                addPDF(pdfUrl, pdfFile, pdfFiles)
                                    
                            pdfFiles_str = ""

                            if doi != "":
                                doi_or_url = doi
                            elif url != "":
                                doi_or_url = url
                            else:
                                doi_or_url = ""

                            # if there is still no PDF then try sci-hub to get one
                            # PS: trying to get PDF files for every BIB seems a bad idea
                            if False and len(pdfFiles) == 0 and doi_or_url != "":
                                # use sci-hub if we have a doi or url

                                # http://dx.doi.org/10.1145/358746.358767
                                # https://dx.doi.org/10.1145/358746.358767
                                # https://www.sciencedirect.com/science/article/pii/S0304397500001006

                                sciHubRoot = "https://sci-hub.se/"
                                sciHub = sciHubRoot + doi_or_url
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

                                        addPDF(pdfUrl, "", pdfFiles)
                                except Exception as e:
                                    print(f"SCIHUB EXCEPT " + e)

                            if len(pdfFiles) == 1:
                                    pdfFiles_str += f'Pdffile: {pdfFiles[0]}\n'
                            elif len(pdfFiles) > 1:
                                for pdfFile in pdfFiles:
                                    pdfFiles_str += f'Pdffiles: {pdfFile}\n'
                            else:
                                # still no PDF file
                                print(f"NOPDF")

                            mdfile = os.path.join("", f"entry-{i}.md")
#Date: {year}\n\
                            NEWLINE = "\n"
                            markdown = f"\
Title: {title}\n\
Year: {year}\n\
Authors: {'; '.join(authors)}\n\
Rootfolder: {cwd}\n\
Bibfile: {os.path.join(cwd, bibFile)}\n\
BibFileName: {bibFile}\n\
Mdfile: {os.path.join(cwd, mdfile)}\n\
{'Journal: ' + journal + NEWLINE if journal != '' else ''}\
{'Booktitle: ' + booktitle + NEWLINE if booktitle != '' else ''}\
{'Date: ' + date_added + NEWLINE if date_added != '' else ''}\
{'Modified: ' + date_modified + NEWLINE if date_modified != '' else ''}\
{'thedoiurl: ' + doi + NEWLINE if doi != '' else ''}\
{'doi: ' + doiNoURL + NEWLINE if doiNoURL != '' else ''}\
{'theurl: ' + url + NEWLINE if url != '' else ''}\
{'Tags: ' + ', '.join(keywords) + NEWLINE if len(keywords) > 0 else ''}\
Key: {key}\n\
Slug: {doiNoURL if doiNoURL != '' else strippedUrl if strippedUrl != '' else key}\n\
engine: knitr\n"

                            if not len(pdfFiles) == 0:
                                # markdown += f"Pdffiles: {'; '.join(pdfFiles)}\n"
                                markdown += pdfFiles_str

                            markdown += "\n"
                            markdown += f"\
    :::bibtex\n\
{bibcontent}\n\
\n\
<bib id=\"bib\">\
{bibcontent}\
</bib>"

                            text_file = open(mdfile, "w")
                            text_file.write(markdown)
                            text_file.close()

                            i = i + 1

authorsFile = open("./docs/authors.txt", "w")
for author in allAuthors:
    authorsFile.write(author + "\n")
authorsFile.close()

keywordsFile = open("./docs/keywords.txt", "w")
for keyword in allKeywords:
    keywordsFile.write(keyword + "\n")
keywordsFile.close()

keysFile = open("./docs/keys.txt", "w")
for key in allKeys:
    keysFile.write(key + "\n")
keysFile.close()

print(f"ERRORS {errors}")