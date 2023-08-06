# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['biopipen',
 'biopipen.core',
 'biopipen.ns',
 'biopipen.scripts.bam',
 'biopipen.scripts.bcftools',
 'biopipen.scripts.bed',
 'biopipen.scripts.gene',
 'biopipen.scripts.misc',
 'biopipen.scripts.scrna_metabolic',
 'biopipen.scripts.vcf',
 'biopipen.scripts.web',
 'biopipen.utils']

package_data = \
{'': ['*'],
 'biopipen': ['reports/bam/*',
              'reports/gsea/*',
              'reports/scrna/*',
              'reports/scrna_metabolic/*',
              'reports/tcr/*',
              'reports/utils/*',
              'reports/vcf/*',
              'scripts/gsea/*',
              'scripts/plot/*',
              'scripts/rnaseq/*',
              'scripts/scrna/*',
              'scripts/tcr/*']}

install_requires = \
['cmdy>=0.5,<0.6',
 'datar>=0.8,<0.9',
 'pipen-filters>=0.1,<0.2',
 'pipen>=0.3,<0.4']

extras_require = \
{'test': ['pipen-verbose>=0.1,<0.2', 'pipen-args>=0.2,<0.3']}

entry_points = \
{'pipen_cli_run': ['bam = biopipen.ns.bam',
                   'bcftools = biopipen.ns.bcftools',
                   'bed = biopipen.ns.bed',
                   'csv = biopipen.ns.csv',
                   'gene = biopipen.ns.gene',
                   'gsea = biopipen.ns.gsea',
                   'misc = biopipen.ns.misc',
                   'plot = biopipen.ns.plot',
                   'rnaseq = biopipen.ns.rnaseq',
                   'scrna = biopipen.ns.scrna',
                   'scrna_metabolic = biopipen.ns.scrna_metabolic',
                   'tcr = biopipen.ns.tcr',
                   'vcf = biopipen.ns.vcf',
                   'web = biopipen.ns.web']}

setup_kwargs = {
    'name': 'biopipen',
    'version': '0.4.6',
    'description': 'Bioinformatics processes/pipelines that can be run from `pipen run`',
    'long_description': None,
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
