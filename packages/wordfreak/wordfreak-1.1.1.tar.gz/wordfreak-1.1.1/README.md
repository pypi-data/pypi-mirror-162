<div align="center">
    <img src="https://raw.githubusercontent.com/joeyagreco/wordfreak/main/img/wordfreak_logo.png" alt="wordfreak logo" width="350"/>


A Python library to extract word frequencies from files.

![Main Build](https://github.com/joeyagreco/wordfreak/actions/workflows/main-build.yml/badge.svg)
![Last Commit](https://img.shields.io/github/last-commit/joeyagreco/wordfreak)

</div>

## Supported File Types

| File Extension | Explanation                       | Supported          |
|----------------|-----------------------------------|--------------------|
| .doc           | Microsoft Word document pre-2007  | :x:                |
| .docx          | Microsoft Word document post-2007 | :heavy_check_mark: |
| .pdf           | Portable Document Format          | :heavy_check_mark: |
| .txt           | Plain text file                   | :heavy_check_mark: |

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install..

```bash
pip install wordfreak
```

## Usage

```python
import wordfreak

# Takes a text source and extracts the word frequencies from it in order from most -> least occurring.
# Extracts word frequencies from "inputFile.txt" and returns them as a Python dictionary.
wordFrequencies = wordfreak.extractWordFrequencies("C:\\inputFile.txt")

# If an output file path is given, it will also save the results there as JSON.
wordFrequencies = wordfreak.extractWordFrequencies("C:\\inputFile.txt", "C:\\outputFile.json")

# Takes a saved word frequencies JSON file and converts it to a Python dictionary.
# Loads word frequencies from "wordFrequencies.json" and returns them as a Python dictionary.
wordFrequencies = wordfreak.pythonizeWordFrequencies("C:\\wordFrequencies.json")
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)