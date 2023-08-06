# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chunkr']

package_data = \
{'': ['*']}

install_requires = \
['fsspec>=2022.7.1,<2023.0.0',
 'paramiko>=2.11.0,<3.0.0',
 'pyarrow>=8.0.0,<9.0.0']

setup_kwargs = {
    'name': 'chunkr',
    'version': '0.1.3',
    'description': 'A library for chunking different types of data files.',
    'long_description': '# chunkr\n[![PyPI version][pypi-image]][pypi-url]\n<!-- [![Build status][build-image]][build-url] -->\n<!-- [![Code coverage][coverage-image]][coverage-url] -->\n<!-- [![GitHub stars][stars-image]][stars-url] -->\n[![Support Python versions][versions-image]][versions-url]\n\n\nA library for chunking different types of data files into another file format. Large files friendly.\n\nCurrently supported input formats: csv, parquet\n\n## Getting started\n\n```bash\npip install chunkr\n```\n\n## Usage\n\n```py\nfrom chunkr import create_chunks_dir\n\nwith create_chunks_dir(file_format, name, input_filepath, output_dir, chunk_size, **extra_args) as chunks_dir:\n    # process chunk files inside dir\n```\n\nparameters:\n\n- format (str): input format (csv, parquet)\n- name (str): a distinct name of the chunking job\n- path (str): the path of the input (local, sftp etc, see fsspec for possible input)\n- output_path (str): the path of the directory to output the chunks to\n- chunk_size (int, optional): number of records in a chunk. Defaults to 100_000.\n- storage_options (dict, optional): extra options to pass to the underlying storage e.g. username, password etc. Defaults to None.\n- write_options (dict, optional): extra options for writing the chunks passed to the respective library. Defaults to None.\n- extra_args (dict, optional): extra options passed on to the parsing system, file specific\n\n>**Note**: currently chunkr only supports parquet as the output chunk files format\n\n## Examples\n\n\n### CSV\n\nSuppose you want to chunk a csv file of 1 million records into 10 parquet pieces, you can do this\n\nCSV extra args are passed to PyArrows [Parsing Options](https://arrow.apache.org/docs/python/generated/pyarrow.csv.ParseOptions.html#pyarrow.csv.ParseOptions)\n\n```py\nfrom chunkr import create_chunks_dir\nimport pandas as pd\n\nwith create_chunks_dir(\n            \'csv\',\n            \'csv_test\',\n            \'path/to/file\',\n            \'temp/output\',\n            100_000,\n            None,\n            None,\n            quote_char=\'"\',\n            delimiter=\',\',\n            escape_char=\'\\\\\',\n    ) as chunks_dir:\n\n        assert 1_000_000 == sum(\n            len(pd.read_parquet(file)) for file in chunks_dir.iterdir()\n        )\n```\n\n### Parquet\n\n```py\nfrom chunkr import create_chunks_dir\nimport pandas as pd\n\nwith create_chunks_dir(\n            \'parquet\',\n            \'parquet_test\',\n            \'path/to/file\',\n            \'temp/output\'\n    ) as chunks_dir:\n\n        assert 1_000_000 == sum(\n            len(pd.read_parquet(file)) for file in chunks_dir.iterdir()\n        )\n```\n\n\n### Reading file(s) inside an archive (zip, tar)\n\n\nreading multiple files from a zip archive is possible, for csv files in `/folder_in_archive/*.csv` within an archive `csv/archive.zip` you can do:\n\n```py\nfrom chunkr import create_chunks_dir\nimport pandas as pd\n\nwith create_chunks_dir(\n            \'csv\',\n            \'csv_test_zip\',\n            \'zip://folder_in_archive/*.csv::csv/archive.zip\',\n            \'temp/output\'\n    ) as chunks_dir:\n\n        assert 1_000_000 == sum(\n            len(pd.read_parquet(file)) for file in chunks_dir.iterdir()\n        )\n```\n\nThe only exception is when particularly reading a csv file from a tar.gz, there can be **only 1 csv file** within the archive:\n\n```py\nfrom chunkr import create_chunks_dir\nimport pandas as pd\n\nwith create_chunks_dir(\n            \'csv\',\n            \'csv_test_tar\',\n            \'tar://*.csv::csv/archive_single.tar.gz\',\n            \'temp/output\'\n    ) as chunks_dir:\n\n        assert 1_000_000 == sum(\n            len(pd.read_parquet(file)) for file in chunks_dir.iterdir()\n        )\n```\n\nbut it\'s okay for other file types like parquet:\n\n\n```py\nfrom chunkr import create_chunks_dir\nimport pandas as pd\n\nwith create_chunks_dir(\n            \'parquet\',\n            \'parquet_test\',\n            \'tar://partition_idx=*/*.parquet::test/parquet/archive.tar.gz\',\n            \'temp/output\'\n    ) as chunks_dir:\n\n        assert 1_000_000 == sum(\n            len(pd.read_parquet(file)) for file in chunks_dir.iterdir()\n        )\n```\n\n### Reading from an SFTP remote system\n\nTo authenticate to the SFTP server, you can pass the credentials via storage_options:\n\n```py\nfrom chunkr import create_chunks_dir\nimport pandas as pd\n\nsftp_path = f"sftp://{sftpserver.host}:{sftpserver.port}/parquet/pyarrow_snappy.parquet"\n\nwith create_chunks_dir(\n            \'parquet\',\n            \'parquet_test_sftp\',\n            sftp_path,\n            \'temp/output\',\n            1000,\n            {\n                "username": "user",\n                "password": "pw",\n            }\n    ) as chunks_dir:\n\n        assert 1_000_000 == sum(\n            len(pd.read_parquet(file)) for file in chunks_dir.iterdir()\n        )\n```\n\n<!-- Badges -->\n\n[pypi-image]: https://img.shields.io/pypi/v/chunkr\n[pypi-url]: https://pypi.org/project/chunkr/\n[build-image]: https://github.com/1b5d/chunkr/actions/workflows/build.yaml/badge.svg\n[build-url]: https://github.com/1b5d/chunkr/actions/workflows/build.yaml\n[coverage-image]: https://codecov.io/gh/1b5d/chunkr/branch/main/graph/badge.svg\n[coverage-url]: https://codecov.io/gh/1b5d/chunkr/\n[stars-image]: https://img.shields.io/github/stars/1b5d/chunkr\n[stars-url]: https://github.com/1b5d/chunkr\n[versions-image]: https://img.shields.io/pypi/pyversions/chunkr\n[versions-url]: https://pypi.org/project/chunkr/\n',
    'author': '1b5d',
    'author_email': '8110504+1b5d@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/1b5d/chunkr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
