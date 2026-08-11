import aspose.words as aw
import os

def convert_md():
    md_path = os.path.abspath("docs/rag_methodology.md")
    doc = aw.Document(md_path)
    # Save as PDF
    doc.save(os.path.abspath("docs/How_Project_Works.pdf"))
    # Save as Word
    doc.save(os.path.abspath("docs/How_Project_Works.docx"))
    print("Successfully generated PDF and Word docs in docs folder.")

if __name__ == "__main__":
    convert_md()
