import glob, os
import contextlib
import bibtexparser as parser
import string
import urllib.parse

@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)

valid_characters = string.ascii_letters + string.digits + string.whitespace + '-,;:łąę\'"./\\ëö()[]áăóüçćášńßéèÉ'

substitutions = {
    "\\'n": "ń",
    "\\l": "ł",
    "\\'a": "á",
    "\\v{s}": "š",
    "\\ss": "ß",
    "\\'e": "é",
    "\\`e": "è",
    "\\'E": "É",
    '\\"e': "ë",
    "\\\"o": "ö",
    "\\'o": "ó",
    "\\'c": "ć",
    "\\u{a}: "ă"
    }

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
    for key, value in substitutions.items():
        str = str.replace(key, value)

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
        title = sanitise(normalise(title))

        year = getValue(fields, "year", "0")

        author = getValue(fields, "author", "N/A")
        author = sanitise(normalise(author))
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

        result.append((key, authors, title, year, date_added, date_modified, doi, url))

    # print(f"RES: {result}")
    return result

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
                        
                        for key, authors, title, year, date_added, date_modified, doi, url in parsebib("./", bibfile):
                            print(f"BIB {authors} - {title}")

                            pdffiles = []
                            for pdffile in os.listdir("./"):
                                if pdffile.endswith(".pdf"):
                                    print(f"PDF {pdffile}")
                                    pdffileEncoded = os.path.join(cwd, pdffile)
                                    # pdffileEncoded = urllib.parse.quote(pdffileEncoded)
                                    pdffiles.append(pdffileEncoded)

                            pdffiles_str = ""
                            if len(pdffiles) == 1: 
                                    pdffiles_str += f'Pdffile: {pdffiles[0]}\n'
                            elif len(pdffiles) > 1:
                                for pdffile in pdffiles:
                                    pdffiles_str += f'Pdffiles: {pdffile}\n'

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

                            if not len(pdffiles) == 0:
                                # markdown += f"Pdffiles: {'; '.join(pdffiles)}\n"
                                markdown += pdffiles_str

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
