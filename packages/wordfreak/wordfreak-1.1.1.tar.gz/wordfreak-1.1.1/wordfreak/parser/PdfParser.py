from PyPDF2 import PdfReader

from wordfreak.parser.Parser import Parser


class PdfParser(Parser):
    """
    For use parsing .pdf files.
    """

    @classmethod
    def getWordFrequency(cls, pathToPdfFile: str) -> dict[str, int]:
        # get all word frequencies from the given .pdf file
        lines = list()
        reader = PdfReader(pathToPdfFile)
        for page in reader.pages:
            lines.append(page.extract_text())
        return cls._getWordFrequencyFromLines(lines)
