import json
from typing import Optional

from wordfreak.parser.DocxParser import DocxParser
from wordfreak.parser.PdfParser import PdfParser
from wordfreak.parser.TxtParser import TxtParser
from wordfreak.util.constants import JSON_FILE_EXTENSION, TXT_FILE_EXTENSION, PDF_FILE_EXTENSION, DOCX_FILE_EXTENSION


def extractWordFrequencies(inputFilePath: str, outputFilePath: Optional[str] = None) -> dict[str, int]:
    """
    Takes a file path and extracts all word frequencies from it as a Python dictionary.

    If outputFilePath is given, it will also save the results to that file as JSON.

    inputFilePath: Path to file to extract work frequencies from.
    outputFilePath: Path to file to save word frequencies to (must be .json file).
    """

    if outputFilePath is not None and not outputFilePath.lower().endswith(JSON_FILE_EXTENSION):
        raise ValueError(f"Output file must be a .json file.")

    if inputFilePath.lower().endswith(TXT_FILE_EXTENSION):
        wordFrequencies = TxtParser.getWordFrequency(inputFilePath)
    elif inputFilePath.lower().endswith(PDF_FILE_EXTENSION):
        wordFrequencies = PdfParser.getWordFrequency(inputFilePath)
    elif inputFilePath.lower().endswith(DOCX_FILE_EXTENSION):
        wordFrequencies = DocxParser.getWordFrequency(inputFilePath)
    else:
        raise ValueError(f"Filetype not supported for parsing (tried to parse file at '{inputFilePath}').")

    # sort word frequencies by number of occurrences
    orderedWordFreq = dict(sorted(wordFrequencies.items(), reverse=True, key=lambda item: item[1]))

    # save to JSON file if requested
    if outputFilePath is not None:
        with open(outputFilePath, "w+") as file:
            json.dump(orderedWordFreq, file)

    return orderedWordFreq


def pythonizeWordFrequencies(jsonFilePath: str) -> dict[str, int]:
    """
    Takes a file path to a JSON file that holds word frequencies and returns it as a Python dictionary.
    After word frequencies have been extracted by extractWordFrequencies(), the resulting JSON file can be fed into this method to Pythonize.

    jsonFilePath: Path to a file to Pythonize (must be .json file).
    """
    with open(jsonFilePath) as json_file:
        wordFrequencies: dict = json.load(json_file)

    # make sure this is a valid word frequencies file/dict
    if not all(isinstance(count, int) for count in wordFrequencies.values()):
        raise ValueError("Word Frequencies not formatted correctly, values must by type 'int'.")

    return wordFrequencies
