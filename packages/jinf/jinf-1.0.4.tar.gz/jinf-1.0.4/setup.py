# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jinf']

package_data = \
{'': ['*'], 'jinf': ['data/*']}

extras_require = \
{'pyknp': ['pyknp[pyknp]>=0.6,<1.0']}

setup_kwargs = {
    'name': 'jinf',
    'version': '1.0.4',
    'description': 'A Japanese inflection converter.',
    'long_description': '# Jinf: Japanese Inflection Converter\n\n[![test](https://img.shields.io/github/workflow/status/hkiyomaru/jinf/test?label=test&logo=Github&style=flat-square)](https://github.com/hkiyomaru/jinf/actions/workflows/test.yml)\n![PyPI](https://img.shields.io/pypi/v/jinf?style=flat-square)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/jinf?style=flat-square)\n![License - MIT](https://img.shields.io/github/license/hkiyomaru/jinf?style=flat-square)\n\n**Jinf** is a Japanese inflection converter.\nJinf depends on [JumanDic](https://github.com/ku-nlp/JumanDIC) and follows the grammar.\n\n## Installation\n\n```shell\npip install jinf\n```\n\n## Usage\n\n```python\nfrom jinf import Jinf\n\njinf = Jinf()\n\ntext = "走る"\ninf_type = "子音動詞ラ行"\nsource_inf_form = "基本形"\nprint(jinf(text, inf_type, source_inf_form, "基本形"))  # 走る\nprint(jinf(text, inf_type, source_inf_form, "未然形"))  # 走ら\nprint(jinf(text, inf_type, source_inf_form, "意志形"))  # 走ろう\nprint(jinf(text, inf_type, source_inf_form, "命令形"))  # 走れ\nprint(jinf(text, inf_type, source_inf_form, "三角形"))  # ValueError: \'三角形\' is not a valid inflection form of \'子音動詞ラ行\'\nprint(jinf(text, inf_type, source_inf_form, "デアル列命令形"))  # ValueError: \'デアル列命令形\' is not a valid inflection form of \'子音動詞ラ行\'\n```\n\n### [pyknp](https://github.com/ku-nlp/pyknp) integration\n\n[pyknp](https://github.com/ku-nlp/pyknp) is the official Python binding for Jumanpp.\nTo enable the pyknp integration, specify the extra requirement when installing Jinf:\n\n```shell\npip install jinf[pyknp]\n```\n\n[Morpheme](https://pyknp.readthedocs.io/en/latest/mrph.html#module-pyknp.juman.morpheme) objects can be used as input for Jinf as follows.\n\n```python\nfrom jinf import Jinf\nfrom pyknp import Morpheme\n\njinf = Jinf()\n\nmrph = Morpheme(\'走る はしる 走る 動詞 2 * 0 子音動詞ラ行 10 基本形 2 "代表表記:走る/はしる"\')\nprint(jinf.convert_pyknp_morpheme(mrph, "基本形"))  # 走る\nprint(jinf.convert_pyknp_morpheme(mrph, "未然形"))  # 走ら\nprint(jinf.convert_pyknp_morpheme(mrph, "意志形"))  # 走ろう\nprint(jinf.convert_pyknp_morpheme(mrph, "命令形"))  # 走れ\nprint(jinf.convert_pyknp_morpheme(mrph, "三角形"))  # ValueError: \'三角形\' is not a valid inflection form of \'子音動詞ラ行\'\nprint(jinf.convert_pyknp_morpheme(mrph, "デアル列命令形"))  # ValueError: \'デアル列命令形\' is not a valid inflection form of \'子音動詞ラ行\'\n```\n\n## List of available inflection types/forms\n\nSee [JUMAN.katuyou](https://github.com/ku-nlp/JumanDIC/blob/master/grammar/JUMAN.katuyou) in [JumanDic](https://github.com/ku-nlp/JumanDIC).\n',
    'author': 'Hirokazu Kiyomaru',
    'author_email': 'h.kiyomaru@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hkiyomaru/jinf',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
