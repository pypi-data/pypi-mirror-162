from setuptools import setup

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='NlpToolkit-InformationRetrieval',
    version='1.0.0',
    packages=['InformationRetrieval',
              'InformationRetrieval.Document',
              'InformationRetrieval.Index',
              'InformationRetrieval.Query'],
    url='https://github.com/StarlangSoftware/InformationRetrieval-Py',
    license='',
    author='olcaytaner',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='Information Retrieval Library',
    install_requires=['NlpToolkit-MorphologicalDisambiguation'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
