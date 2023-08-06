import docx2txt

from wordfreak.parser.Parser import Parser


class DocxParser(Parser):
    """
    For use parsing .docx files.
    """

    @classmethod
    def getWordFrequency(cls, pathToPdfFile: str) -> dict[str, int]:
        # get all word frequencies from the given .docx file
        lines = docx2txt.process(pathToPdfFile).split()
        return cls._getWordFrequencyFromLines(lines)
