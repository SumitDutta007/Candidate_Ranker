import io
import docx
import PyPDF2


class DocumentLoader:

    @staticmethod
    def load(uploaded_file):

        name = uploaded_file.name.lower()

        if name.endswith(".txt") or name.endswith(".md"):
            return uploaded_file.read().decode("utf-8")

        if name.endswith(".pdf"):

            pdf = PyPDF2.PdfReader(uploaded_file)

            text = ""

            for page in pdf.pages:
                text += page.extract_text() or ""

            return text

        if name.endswith(".docx"):

            doc = docx.Document(
                io.BytesIO(
                    uploaded_file.read()
                )
            )

            return "\n".join(
                para.text
                for para in doc.paragraphs
            )

        raise ValueError(
            "Unsupported JD file type"
        )