# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['liftover_bam']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0', 'pysam==0.18.0']

setup_kwargs = {
    'name': 'liftover-bam',
    'version': '0.1.0',
    'description': 'A simple module to liftover bam alignments',
    'long_description': '# Lifting over bam #\n\n[![poetry CI](https://github.com/wckdouglas/liftover_bam/actions/workflows/ci.yml/badge.svg)](https://github.com/wckdouglas/liftover_bam/actions/workflows/ci.yml)\n\nSometimes for amplicon sequencings, we would like to map reads to the amplicon sequence only but bringing them back to genomic coordinates for easy variant calling and viewing.\n\nLet\'s say we have a gene in `chr1:100-1000`, and we would first extract this locus from the genome fasta file to make a new fasta record with name `>chr1:100-1000`, this can be done with:\n```\necho "chr1:100-1000" | samtools faidx -r - genome.fa > gene.fa \n```\nand map the reads to this single gene fasta file with `bwa` or `bowtie2` to make a bam alignment file:\n```\nbwa mem gene.fa query.fq | samtools view -b > gene.bam\n```\n\nSo what if you want to put these alignments back to the genomic coordinates after that?\n\nThe `liftover_bam.liftover` function is trying to solve this problem in pure python!\n\n```\ngene_bam="gene.bam"\ngenome_bam="any.bam_file_that_maps_to_the_genome"\nout_bam="where_you_want_your_output_bam_file_to_be"\nliftover(gene_bam, genome_bam, out_bam)\n```\n',
    'author': 'Douglas Wu',
    'author_email': 'wckdouglas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
