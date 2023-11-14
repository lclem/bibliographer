#!/usr/bin/python3

from pypdf import PdfReader, PdfWriter, generic

def isDOI(uri):
    return "doi.org" in uri

def rewriteURI(uri):

    if not isDOI(uri):
        return uri

    # https://doi.org/10.4230/LIPIcs.FSTTCS.2010.1
    parts = uri.split("/")

    if len(parts) < 2:
        return uri

    doi = parts[-2] + "/" + parts[-1]
    uri = f"https://lclem.github.io/bibliographer/articles/{doi}"
    return uri


reader = PdfReader("test.pdf")
writer = PdfWriter()
# print(reader)

for page in reader.pages:
    annotations = page.annotations

    for annot in annotations:
        obj = annot.get_object()
        if "/A" in obj:
            A = obj["/A"]
            # print(A)
            # {'/S': '/GoTo', '/D': 'section*.18'}
            # {'/Type': '/Action', '/S': '/URI', '/URI': 'https://doi.org/10.4230/LIPIcs.FSTTCS.2010.1'}

            if "/URI" in A:
                uri = A["/URI"]
                new_uri = rewriteURI(uri)

                if uri == new_uri:
                    print(f"URI {uri}")
                else:
                    print(f"URI {uri} --> {new_uri}")

                key   = generic.TextStringObject("/URI")
                value = generic.TextStringObject(new_uri)
                obj['/A'][key] = value

    # del page['/Annots']
    writer.add_page(page)

writer.write("test-new.pdf")
writer.close()