# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bb_wrapper', 'bb_wrapper.models', 'bb_wrapper.services', 'bb_wrapper.wrapper']

package_data = \
{'': ['*']}

install_requires = \
['Unidecode>=1.2.0,<2.0.0',
 'crc>=1.0.1,<2.0.0',
 'pycpfcnpj>=1.5.1,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'python-barcode>=0.13.1,<0.14.0',
 'python-decouple>=3.4,<4.0',
 'qrcode>=7.3,<8.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'bb-wrapper',
    'version': '0.4.5',
    'description': 'Cliente não oficial da API do Banco do Brasil',
    'long_description': "Cliente não oficial feito em Python, para realizar integração com as API's do Banco do Brasil.\n\n`Documentação oficial do BB <https://developers.bb.com.br/>`_\n\nInstalando\n===========\n\nNosso pacote está hospedado no `PyPI <https://pypi.org/project/bb-wrapper/>`_\n\n.. code-block:: bash\n\n    pip install bb-wrapper\n\n\n\nConfiguração\n==================\nPara utilizar o `bb-wrapper` é necessário ter algumas constantes/variáveis. sendo elas:\n\n.. code-block:: python\n\n    IMOBANCO_BB_IS_SANDBOX='flag True ou False para indicar utilização de sandbox ou não'\n    IMOBANCO_BB_BASIC_TOKEN='chave de autenticação gerada para a aplicação no site developers.bb'\n    IMOBANCO_BB_GW_APP_KEY='chave de desenvolvimento gerada para a aplicação no site developers.bb'\n\n\nPara geração de boletos é necessário:\n\n.. code-block:: python\n\n    IMOBANCO_BB_CONVENIO='convênio do contrato para geração de boletos'\n    IMOBANCO_BB_CARTEIRA='carteira do contrato para geração de boletos'\n    IMOBANCO_BB_VARIACAO_CARTEIRA='variação da carteira do contrato para geração de boletos\n    IMOBANCO_BB_AGENCIA='agência da conta berço do contrato para geração de boletos'\n    IMOBANCO_BB_CONTA='nº da conta berço do contrato para geração de boletos'\n\n\nRecomendamos criar um arquivo `.env` contendo essas varíaveis de ambiente.\n\n::\n\n    Podem ser criadas diretamente no terminal (não recomendado).\n\n    Podem ser criadas também diretamente no `arquivo.py` (não recomendado).\n\nRecursos disponíveis\n=====================\n\nAPI's\n---------------------\n\n- ☑ API de Cobrança (geração de boletos)\n- ☑ API PIX (recebimento PIX) {essa API ainda está instável e incompleta no BB}\n- ☐ API Arrecadação PIX {sem previsão de implementação}\n- ☑ API Lotes de Pagamentos {essa API ainda está instável e incompleta no BB}\n\n  - ☐ Transferência PIX\n  - ☑ Transferência Bancária\n  - ☐ Pagamento GPS\n  - ☐ Pagamento GRU\n  - ☐ Pagamento DARF Preto\n  - ☑ Pagamento Tributos\n  - ☑ Pagamento Boletos\n\nRecursos auxiliares\n-------------------\n\n- ☑ Geração de imagem b64\n- ☑ Geração, validação e conversão de código de barras de boleto\n- ☑ Geração, validação e conversão de código de barras de tributos\n- ☑ Geração de QR Code PIX\n- ☑ Validação e limpeza de CPF/CNPJ\n\nExemplos disponíveis\n=====================\nExistem exemplos de utilização da biblioteca na pasta `examples`.\n\nPreparando ambiente de desenvolvimento\n=======================================\n\n> O Nix é utilizado para gerenciar os pacotes necessários, por exemplo como a versão correta do python.\n\nCertifique-se que o ambiente está ativado, se não estiver execute:\n\n.. code-block:: bash\n\n    nix develop\n\n",
    'author': 'Imobanco',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/imobanco/bb-wrapper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
