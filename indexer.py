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

valid_characters = string.ascii_letters + string.digits + string.whitespace + '-'

def sanitise(str):
    result = "".join(c for c in str if c in valid_characters)
    return result.encode('utf-8').decode("ascii", "ignore")

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
        key = entry.key
        key = key.encode('utf-8').decode("ascii", "ignore")
        
        title = sanitise(fields['title'].value if 'title' in fields else "N/A")
        
        year = fields['year'].value if 'year' in fields else "0"

        author = sanitise(fields['author'].value if 'author' in fields else "N/A")
        authors = author.split(" and ")

        result.append((key, authors, title, year))

    # print(f"key {entry.key}, type {entry.entry_type}, fields {entry.fields_dict} \n")

    return result

for root, dirs, files in os.walk("./library"):
    i = 0
    for dir in dirs:
        cwd = os.path.join(root, dir)
        with pushd(cwd):
            print(f"CWD {os.getcwd()}")
            for _, _, files in os.walk("./"):
                for file in files:
                    if file.endswith(".bib"):
                        bibfile = file # os.path.join(root, file)

                        text_file = open(bibfile, "r")
                        bibcontent = text_file.read()
                        text_file.close()
                        
                        for key, authors, title, year in parsebib("./", bibfile):
                            print(f"BIB {authors} - {title} - {year}")

                            # pdfline = ""
                            # for pdffile in os.listdir("./"):
                            #     if pdffile.endswith(".pdf"):
                            #         print(f"PDF {pdffile}")
                            #         pdfline = f"PDF: {os.path.join(cwd, pdffile)}"
                            #         break

                            mdfile = os.path.join("", f"entry-{i}.md")
#Date: {year}\n\

                            markdown = f"\
Title: {title}\n\
Year: {year}\n\
Authors: {'; '.join(authors)}\n\
Bibfile: {os.path.join(cwd, bibfile)}\n\
Key: {key}\n\
Slug: {key}\n\n\
\
````{{verbatim}}\n\
{bibcontent}\n\
````"
                            #markdown = markdown + pdfline
                            text_file = open(mdfile, "w")
                            text_file.write(markdown)
                            text_file.close()

                            i = i + 1