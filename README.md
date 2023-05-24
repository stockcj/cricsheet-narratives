# Cricsheet Narratives
This Python module provides functions to convert [Cricsheet](https://cricsheet.org/) JSON files into human-readable narrative txt files. It includes functions for reading the JSON files, creating headers, generating remarks for each delivery, formatting overs and innings, creating the match narrative, and generating the final output.

The project was developed as a hobby to produce narrative accounts of matches that could be used for practising scoring. Similar to the files provided in the [ECB ACO Basics of Scoring course](https://www.ecb.co.uk/be-involved/officials/find-a-course/scorers-count).

I may make updates to the project, but it's not maintained.

## Dependencies
The module was developed using Python 3.11

* json: Provides functions for working with JSON data.
* os: Provides functions for working with operating systems.
* datetime: Provides classes for manipulating dates and times.
* [prettytable](https://github.com/jazzband/prettytable): A library for displaying tabular data in a visually appealling ASCII table format.

## Usage
Install the dependencies listed in the Pipfile, then run the module and enter the path to a folder containing .json files downloaded from Cricsheet.

## License
This module is released under the GNU General Public License. See the LICENSE file for more details.