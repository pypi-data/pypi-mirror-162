# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['similarnames']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'similarnames',
    'version': '0.1.3',
    'description': 'Library for Standardizing names from a Pandas dataframe',
    'long_description': '# Similar Names\nLibrary for Standardizing names from a Pandas dataframe\n\n## Description\nSimilar Names is basically a package for names manipulation. That is, if you have a Pandas dataframe with multiple names written in different ways (e.g.: John Doe, John E. Doe and John Edson Doe), the "closeMatches" function will look for all similar names on that column and then add two columns: "Close Matches" (list of all close matches) and "StandardName" (shortest name of the list).\n\n## Instalation\nSimilar Names can be installed directly through pip\n`pip install similarnames`\n\n## How to use?\nIf you have a pandas dataframe with the names that you want to standardize, or look for close matches, simply execute the following command.\n\n```python\n\'\'\'\nInput (df): df and the name of the column with the names to check\n\n| Names          | ... |\n|----------------|-----|\n| John Doe       |     |\n| John Edson Doe |     |\n| John E. Doe    |     |\n| John Edson D.  |     |\n\'\'\'\nfrom similarnames import closeMatches\n\ndf_standard = closeMatches(df, \'Names\')\n\n\'\'\'\nOutput (df_standard)\n\n| Names          | ... | CloseMatches                                                   | StandardName |\n|----------------|-----|----------------------------------------------------------------|--------------|\n| John Doe       |     | [\'John Doe\', \'John E. Doe\', \'John Edson Doe\', \'John Edson D.\'] | John Doe     |\n| John Edson Doe |     | [\'John Doe\', \'John E. Doe\', \'John Edson Doe\', \'John Edson D.\'] | John Doe     |\n| John E. Doe    |     | [\'John Doe\', \'John E. Doe\', \'John Edson Doe\', \'John Edson D.\'] | John Doe     |\n| John Edson D.  |     | [\'John Doe\', \'John E. Doe\', \'John Edson Doe\', \'John Edson D.\'] | John Doe     |\n\n\'\'\'\n```\n\nIn case you have multiple names in a single row, the "explode" is automatically done for you. So, just provide the "sep" parameter to identify where we should use to split those names. Note: If you have an "and" (e.g.: Jon and Jane), it will be automatically replaced by the "sep" parameter before the split.\n\n```python\n\'\'\'\nInput (df): df and the name of the column with the names to check\n\n| Names                                        | Other columns           | ... |\n|----------------------------------------------|-------------------------|-----|\n| John Doe, Jane Doe                           | Two names (sep = \',\')   |     |\n| John E. Doe and Michael Johnson              | Two names (without sep) |     |\n| Jane A. Doe, Michael M. Johnson and John Doe | Three names (sep = \',\') |     |\n\'\'\'\nfrom similarnames import closeMatches\n\ndf_standard = closeMatches(df, \'Names\', sep = \',\')\n\n\'\'\'\nOutput (df_standard)\n\n| Names              | Other columns           | ... | CloseMatches                              | StandardName    |\n|--------------------|-------------------------|-----|-------------------------------------------|-----------------|\n| John Doe           | Two names (sep = \',\')   |     | [\'John Doe\', \'John E. Doe\']               | John Doe        |\n| Jane Doe           | Two names (sep = \',\')   |     | [\'Jane Doe\', \'Jane A. Doe\']               | Jane Doe        |\n| John E. Doe        | Two names (without sep) |     | [\'John Doe\', \'John E. Doe\']               | John Doe        |\n| Michael Johnson    | Two names (without sep) |     | [\'Michael Johnson\', \'Michael M. Johnson\'] | Michael Johnson |\n| Jane A. Doe        | Three names (sep = \',\') |     | [\'Jane Doe\', \'Jane A. Doe\']               | Jane Doe        |\n| Michael M. Johnson | Three names (sep = \',\') |     | [\'Michael Johnson\', \'Michael M. Johnson\'] | Michael Johnson |\n| John Doe           | Three names (sep = \',\') |     | [\'John Doe\', \'John E. Doe\']               | John Doe        |\n\n\'\'\'\n```\n',
    'author': 'paulobrunheroto',
    'author_email': 'paulobrunheroto@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/paulobrunheroto/similarnames',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
