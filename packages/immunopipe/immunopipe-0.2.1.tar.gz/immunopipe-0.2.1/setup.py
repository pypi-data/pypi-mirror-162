# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['immunopipe']

package_data = \
{'': ['*'], 'immunopipe': ['reports/*', 'scripts/*']}

install_requires = \
['biopipen>=0.4,<0.5',
 'datar>=0.8,<0.9',
 'pipen-args>=0.2,<0.3',
 'pipen-filters>=0.1,<0.2',
 'pipen-report>=0.4,<0.5',
 'pipen-verbose>=0.1.0,<0.2.0']

entry_points = \
{'console_scripts': ['immunopipe = immunopipe.pipeline:main']}

setup_kwargs = {
    'name': 'immunopipe',
    'version': '0.2.1',
    'description': 'A pipeline for integrative analysis for scTCR- and scRNA-seq data',
    'long_description': '# immunopipe\n\nIntegrative analysis for scTCR- and scRNA-seq data\n\n## Requirements & Installation\n\n- `python`: `3.7+`\n    - Other python depedencies should be installed via `pip install -U immunopipe`\n\n- `R`\n    - A bunch of R packages\n\n- Other\n  - VDJtools: https://vdjtools-doc.readthedocs.io/en/master/install.html\n\n- Checking requirements\n\n  ```shell\n  pip install -U pipen-cli-require\n  pipen require immunopipe.pipeline:pipeline <pipeline arguments>\n  ```\n\n- Quick way to install the dependencies using conda\n  ```shell\n  conda env create --file docker/environment.yml\n  # then\n  conda activate immunopipe\n  ```\n\n## Running as a container\n\n### Using docker:\n\n```bash\ndocker run -w /workdir -v .:/workdir -it justold/immunopipe:dev\n```\n\n### Using singularity:\n\n```bash\nsingularity run -w \\  # need it to be writable\n  -H /home/immunopipe_user \\  # required, used to init conda\n  --pwd /workdir -B .:/workdir \\  # Could use other directory instead of "."\n  # --contain: don\'t map host filesystem\n  # --cleanenv: recommended, to avoid other host\'s environment variables to be used\n  #   For example, $CONDA_PREFIX to affect host\'s conda environment\n  --contain --cleanenv \\\n  docker://justold/immunopipe:dev\n\n# The mount your data directory to /mnt, which will make startup faster\n# For example\n#   -B .:/workdir,/path/to/data:/mnt\n# Where /path/to/data is the data directory containing the data files\n# You may also want to bind other directories (i.e. /tmp)\n#   -B <other bindings>,/tmp\n\n# Or you can pull the image first by:\nsingularity pull --force --dir images/ docker://justold/immunopipe:dev\n# Then you can replace "docker://justold/immunopipe:dev" with "images/immunopipe.sif"\n```\n\n## Modules\n\n- Basic TCR data analysis using `immunarch`\n- Clone Residency analysis if you have paired samples (i.e. Tumor vs Normal)\n- V-J usage, the frequency of various V-J junctions in circos-style plots\n- Clustering cells and configurale arguments to separate T and non-T cells\n- Clustering T cell, markers for each cluster and enrichment analysis for the markers\n- Radar plots to show the composition of cells for clusters\n- (Meta-)Markers finder for selected groups/clones of cells\n- Psedo-bulk GSEA analysis of two groups of cells\n- Seurat cluster statistics, including:\n  - Basic statistics of the clusters (e.g. number of cells in each cluster)\n  - Gene expressions (e.g. ridge, violin, feature, dot and heatmap plots)\n  - Dimensional reduction plots\n- TCR clustering using CDR3 sequences and the statistics of the clusters\n- Cell group distribution (TCR clones/clusters) in Seurat clusters\n- Clone heterogeneity (TCR clone distribution) in Seurat clusters\n- Metabolic landscape analysis (Ref: Xiao, Zhengtao, Ziwei Dai, and Jason W. Locasale. "Metabolic landscape of the tumor microenvironment at single cell resolution." Nature communications 10.1 (2019): 1-12.)\n\n## Documentaion\n\nhttps://pwwang.github.io/immunopipe\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pwwang/immunopipe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
