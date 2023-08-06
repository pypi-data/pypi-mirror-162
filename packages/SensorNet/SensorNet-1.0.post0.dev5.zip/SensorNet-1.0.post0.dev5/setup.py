"""Setup configuration. Nothing here, refer to setup.cfg file."""
import setuptools

import pypandoc
import versioneer

pypandoc.download_pandoc()

try:
    long_description = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setuptools.setup(
    version=versioneer.get_versions(),
    cmdclass=versioneer.get_cmdclass(),
    long_description=long_description,
)
