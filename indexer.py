import glob, os
import contextlib
import bibtexparser as parser
import string

@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)

valid_characters = string.ascii_letters + string.digits + string.whitespace + '-,;:ł'

def sanitise(str):
    result = "".join(c for c in str if c in valid_characters)
    return result.encode('utf-8').decode("ascii", "ignore")

def normalise_author(author):
    names = author.split(", ")
    names = names[1:] + [names[0]]
    return " ".join(names)

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

        print(f"FIELDS: {fields}")
        # print(f"key {entry.key}, type {entry.entry_type}, fields {entry.fields_dict} \n")

        key = entry.key
        key = key.encode('utf-8').decode("ascii", "ignore")
        
        title = sanitise(fields['Title'].value if 'Title' in fields else "N/A")
        
        year = fields['Year'].value if 'Year' in fields else "0"

        author = sanitise(fields['Author'].value if 'Author' in fields else "N/A")
        authors = author.split(" and ")

        for i in range(0, len(authors)):
            authors[i] = normalise_author(authors[i])

        date_added = fields['date-added'].value if 'date-added' in fields else ""
        date_modified = fields['date-modified'].value if 'date-modified' in fields else ""
        doi = fields['DOI'].value if 'DOI' in fields else ""

        result.append((key, authors, title, year, date_added, date_modified, doi))

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
                        
                        for key, authors, title, year, date_added, date_modified, doi in parsebib("./", bibfile):
                            print(f"BIB {authors} - {title}")

                            pdffiles = []
                            for pdffile in os.listdir("./"):
                                if pdffile.endswith(".pdf"):
                                    print(f"PDF {pdffile}")
                                    pdffiles.append(os.path.join(cwd, pdffile))

                            pdffiles_str = ""
                            if len(pdffiles) == 1: 
                                    pdffiles_str += f'Pdffile: {pdffiles[0]}\n'
                            elif len(pdffiles) > 1:
                                for pdffile in pdffiles:
                                    pdffiles_str += f'Pdffiles: {pdffile}\n'

                            mdfile = os.path.join("", f"entry-{i}.md")
#Date: {year}\n\
                            markdown = f"\
Title: {title}\n\
Year: {year}\n\
Authors: {'; '.join(authors)}\n\
Bibfile: {os.path.join(cwd, bibfile)}\n\
{'Date: ' + date_added if date_added != '' else ''}\n\
{'Modified: ' + date_modified if date_modified != '' else ''}\n\
{'DOI: ' + doi if doi != '' else ''}\n\
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