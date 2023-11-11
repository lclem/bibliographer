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
# import werkzeug

# def get_filename(url: str):
#     try:
#         with requests.get(url) as req:
#             if content_disposition := req.headers.get("Content-Disposition"):
#                 param, options = werkzeug.http.parse_options_header(content_disposition)
#                 if param == 'attachment' and (filename := options.get('filename')):
#                     return filename

#             path = urlparse(req.url).path
#             name = path[path.rfind('/') + 1:]
#             return name
#     except requests.exceptions.RequestException as e:
#         raise e

@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)

substitutions = {
    r"\\'\s*a": "á",
    r"\\=\s*a": "ā",
    r"\\u\s*a": "ă",
    r'\\"\s*a': "ä",
    r'\\c\s*a': "ą",
    r"\\v\s*c": "č",
    r"\\'\s*c": "ć",
    r"\\c\s*c": "ç",
    r"\\v\s*C": "Č",
    r"\\ss": "ß",
    r"\\'\s*e": "é",
    r"\\'\s*E": "É",
    r"\\`\s*e": "è",
    r"\\k\s*e": "ę",
    r'\\"\s*e': "ë",
    r"\\'\s*\\i": "í",
    r"\\l": "ł",
    r"\\L": "Ł",
    r'\\"\s*o': "ö",
    r"\\'\s*o": "ó",
    r"\\^\s*o": "ô",
    r"\\o": "ø",
    r"\\'\s*n": "ń",
    r"\\v\s*r": "ř",
    r"\\v\s*s": "š",
    r'\\"\s*u': "ü",
    r"\\.\s*z": "ż"
}

valid_characters = string.ascii_letters + string.digits + string.whitespace + '`-,;:\'"./\\()[]' + "".join(substitutions.values())

def sanitise(str):
    result = "".join(c for c in str if c in valid_characters)
    return result.encode('utf-8').decode("utf-8", "ignore")

def normalise_names_order(author):
    names = author.split(", ")
    names = names[1:] + [names[0]]
    names = " ".join(names)

    return names

def normalise(str):

    orig = str
    str = re.sub(r"\s+", " ", str)
    str = sanitise(str)

    for key, value in substitutions.items():
        # str = str.replace(key, value)
        str = re.sub(key, value, str)

    # print(f"normalise {orig} => {str}\n")
    return str

def getValue(dict, key, default):
    if key in dict:
        return dict[key].value
    else:
        return default

def parsebib(root, bibfile):
    library = parser.parse_file(bibfile)

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

        date_added = getValue(fields, 'date-added', "")
        date_modified = getValue(fields, 'date-modified', "")

        url = getValue(fields, 'url', "")
        url = url.strip()

        doi = getValue(fields, 'doi', "")
        doi = doi.strip()

        if doi != "" and not doi.startswith("http"):
            doi = f"http://dx.doi.org/{doi}"

        eprint = getValue(fields, 'eprint', "")
        journal = getValue(fields, 'journal', "")

        result.append((key, authors, title, year, date_added, date_modified, doi, url, eprint, journal))

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

for root, dirs, files in os.walk("./library/entries"):
    i = 0
    for dir in dirs:
        cwd = os.path.join(root, dir)
        with pushd(cwd):
            print(f"CWD {os.getcwd()}")
            for _, _, files in os.walk("./"):
                for file in files:
                    if file.endswith(".bib"):
                        bibfile = file # os.path.join(root, file)
                        # print(f"FILE {bibfile}")

                        text_file = open(bibfile, "r")
                        bibcontent = text_file.read().strip()
                        text_file.close()

                        biblines = bibcontent.split("\n")
                        for j in range(0, len(biblines)):
                            biblines[j] = "    " + biblines[j]

                        bibcontent = "\n".join(biblines)
                        
                        for key, authors, title, year, date_added, date_modified, doi, url, eprint, journal in parsebib("./", bibfile):
                            print(f"BIB {authors} - {title}")

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

                            if len(pdfFiles) == 0 and doi_or_url != "":
                                # use sci-hub if we have a doi or url

                                # http://dx.doi.org/10.1145/358746.358767
                                # https://www.sciencedirect.com/science/article/pii/S0304397500001006

                                sciHubRoot = "https://sci-hub.se/"
                                sciHub = sciHubRoot + doi_or_url
                                print(f"SCIHUB URL {sciHub}")

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
Bibfile: {os.path.join(cwd, bibfile)}\n\
Mdfile: {os.path.join(cwd, mdfile)}\n\
{'Date: ' + date_added + NEWLINE if date_added != '' else ''}\
{'Modified: ' + date_modified + NEWLINE if date_modified != '' else ''}\
{'DOI: ' + doi + NEWLINE if doi != '' else ''}\
{'THEURL: ' + url + NEWLINE if url != '' else ''}\
Key: {key}\n\
Slug: {key}\n\
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
