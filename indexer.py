import glob, os
import contextlib
import bibtexparser as parser

@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)

def parsebib(root, bibfile):
    library = parser.parse_file(bibfile)

    # print(f"Parsed {len(library.blocks)} blocks, including:"
    #     f"\n\t{len(library.entries)} entries"
    #     f"\n\t{len(library.comments)} comments"
    #     f"\n\t{len(library.strings)} strings and"
    #     f"\n\t{len(library.preambles)} preambles")

    # Comments have just one specific attribute
    first_comment = library.comments[0]
    first_comment.comment # The comment string

    entry = library.entries[0]
    author = entry.fields_dict['author'].value
    title = entry.fields_dict['title'].value
    year = entry.fields_dict['year'].value

    # print(f"key {entry.key}, type {entry.entry_type}, fields {entry.fields_dict} \n")

    # Each field of the entry is a `bibtexparser.model.Field` instance
    first_field = entry.fields[0]
    first_field.key # The field key, e.g. "author"
    first_field.value # The field value, e.g. "Albert Einstein and Boris Johnson"

    return author, title, year

for root, dirs, files in os.walk("./library"):
    for dir in dirs:
        cwd = os.path.join(root, dir)
        with pushd(cwd):
            print(f"CWD {os.getcwd()}")
            for _, _, files in os.walk("./"):
                for file in files:
                    if file.endswith(".bib"):
                        bibfile = file # os.path.join(root, file)
                        # print(f"{bibfile}")
                        author, title, year = parsebib("./", bibfile)
                        print(f"BIB {author} - {title} - {year}")

                        pdfline = ""
                        for pdffile in os.listdir("./"):
                            if pdffile.endswith(".pdf"):
                                print(f"PDF {pdffile}")
                                pdfline = f"PDF: {os.path.join(cwd, pdffile)}"
                                break

                        mdfile = os.path.join("", "entry.md")

                        markdown = f"\
Title: {title}\n\
Year: {year}\n\
Author: {author}\n"
                        markdown = markdown + pdfline
                        text_file = open(mdfile, "w")
                        text_file.write(markdown)
                        text_file.close()