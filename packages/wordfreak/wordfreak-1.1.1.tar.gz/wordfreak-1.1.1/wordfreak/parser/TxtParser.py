from wordfreak.parser.Parser import Parser
from wordfreak.util.constants import UTF_8


class TxtParser(Parser):
    """
    For use parsing .txt files.
    """

    @classmethod
    def getWordFrequency(cls, pathToTxtFile: str) -> dict[str, int]:
        # get all word frequencies from the given .txt file
        with open(pathToTxtFile, encoding=UTF_8) as file:
            lines = file.readlines()
        return cls._getWordFrequencyFromLines(lines)
