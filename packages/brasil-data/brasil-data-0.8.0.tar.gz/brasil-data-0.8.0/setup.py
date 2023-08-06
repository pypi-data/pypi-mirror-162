# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['brdata', 'brdata.cvm']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'beautifulsoup4>=4.10.0,<5.0.0',
 'cachier>=1.5.3,<2.0.0',
 'html5lib>=1.1,<2.0',
 'lxml>=4.6.4,<5.0.0',
 'pandas>=1.3.5,<2.0.0',
 'random-user-agent>=1.0.1,<2.0.0',
 'requests>=2.23.0,<3.0.0',
 'xlrd>=2.0.1,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=4.5.0,<5.0.0']}

setup_kwargs = {
    'name': 'brasil-data',
    'version': '0.8.0',
    'description': 'Fontes de dados do mercado financeiro brasileiro',
    'long_description': '<p align="center">\n  <a href="https://github.com/gabrielguarisa/brdata"><img src="https://raw.githubusercontent.com/gabrielguarisa/brdata/0bd34000bf29bd5b93aee011f368bc0385680c58/logo.png?token=GHSAT0AAAAAABPPKYT7BQBOVDJG3NYYQKNOYQ5JIZA" alt="brdata"></a>\n</p>\n<p align="center">\n    <em>Fontes de dados do mercado financeiro brasileiro</em>\n</p>\n\n<div align="center">\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/gabrielguarisa/brdata/releases)\n[![License](https://img.shields.io/github/license/gabrielguarisa/brdata)](https://github.com/gabrielguarisa/brdata/blob/main/LICENSE)\n\n</div>\n\n## Instalação\n\n```shell\npip install brasil-data\n```\n\n## Utilização\n\n### XPI\n\nColetando dados da análise da XPI para uma determinada ação:\n\n```python\nfrom brdata import xpi\nxpi.analise("cyre3")\n```\n\n### Fundamentus\n\nColetando tabela do resultado da busca no Fundamentus (equivalenta a página https://www.fundamentus.com.br/resultado.php):\n\n```python\nfrom brdata import fundamentus\nfundamentus.resultados()\n```\n\nBalanços históricos de uma determinada ação:\n\n```python\nbalanco, demonstrativo = fundamentus.balanco_historico("mglu3")\n```\n\nDetalhes de uma ação:\n\n```python\nfundamentus.detalhes("mglu3")\n```\n\n### CVM\n\n\nImportando módulo:\n\n```python\nfrom brdata import cvm\n```\n\nBaixando os arquivos de dados:\n\n```python\ncvm.download_data("data")\n```\n\nBaixando os arquivos de metadados:\n\n```python\ncvm.download_metadata("data")\n```\n\n#### Formulário Cadastral\n\nUsando dados do [formulário cadastral](https://dados.gov.br/dataset/cia_aberta-doc-fca):\n\n```python\ng_fca = cvm.GeralFCA("data")\nvm_fca = cvm.ValorMobiliarioFCA("data")\n```\n\nConsultando dados para uma determinada companhia:\n\n```python\ng_fca.get_cia(cvm_code=14460)\n# OU\ng_fca.get_cia(cnpj="47.960.950/0001-21")\n```\n\nNúmero de companhias cadastradas por ano:\n\n```python\ng_fca.get_num_cias_per_year()\n```\n\nQuantidade de empresas cadastradas por setor em cada ano:\n\n```python\ng_fca.get_sectors_per_year()\n```\n\n#### Formulário de Referência\n\nUsando dados do [formulário de referência](https://dados.gov.br/dataset/cia_aberta-doc-fre):\n\n```python\ncvm.DistribuicaoCapitalFRE("data")\n```\n\nConsultando dados para uma determinada companhia:\n\n```python\nd_fre.get_cia("47.960.950/0001-21")\n```\n\n### B3\n\nImportando módulo:\n\n```python\nfrom brdata import b3\n```\n\nÍndices disponíveis:\n\n```python\nb3.indices()\n```\n\nColetando composição de um índice:\n\n```python\nb3.portfolio("ibov")\n```\n\nListando empresas disponíveis na B3:\n\n```python\nb3.cias()\n```\n\nListando todas as BDRs disponíveis:\n\n```python\nb3.bdrs()\n```\n\nDetalhamento de uma empresa:\n\n```python\nb3.detalhes(cvm_code="25135")\n```\n\n### Valor Econômico\n\nImportando módulo:\n\n```python\nfrom brdata import valor\n```\n\nPortfólios das instituições financeiras:\n\n```python\nvalor.portfolios(2, 2022)\n```\n\nCarteira Valor:\n\n```python\nvalor.carteira_valor(2, 2022)\n```',
    'author': 'Gabriel Guarisa',
    'author_email': 'gabrielguarisa@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gabrielguarisa/brdata',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.12,<3.11',
}


setup(**setup_kwargs)
