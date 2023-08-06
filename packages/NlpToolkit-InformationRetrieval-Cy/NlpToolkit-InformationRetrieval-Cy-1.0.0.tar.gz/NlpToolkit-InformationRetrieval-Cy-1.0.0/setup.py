from setuptools import setup

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["InformationRetrieval/Document/*.pyx",
                           "InformationRetrieval/Document/*.pxd",
                           "InformationRetrieval/Index/*.pyx",
                           "InformationRetrieval/Index/*.pxd",
                           "InformationRetrieval/Query/*.pyx",
                           "InformationRetrieval/Query/*.pxd"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-InformationRetrieval-Cy',
    version='1.0.0',
    packages=['InformationRetrieval',
              'InformationRetrieval.Document',
              'InformationRetrieval.Index',
              'InformationRetrieval.Query'],
    package_data={'InformationRetrieval': ['*.pxd', '*.pyx', '*.c'],
                  'InformationRetrieval.Document': ['*.pxd', '*.pyx', '*.c'],
                  'InformationRetrieval.Index': ['*.pxd', '*.pyx', '*.c'],
                  'InformationRetrieval.Query': ['*.pxd', '*.pyx', '*.c']},
    url='https://github.com/StarlangSoftware/InformationRetrieval-Cy',
    license='',
    author='olcaytaner',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='Information Retrieval Library',
    install_requires=['NlpToolkit-MorphologicalDisambiguation-Cy'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
