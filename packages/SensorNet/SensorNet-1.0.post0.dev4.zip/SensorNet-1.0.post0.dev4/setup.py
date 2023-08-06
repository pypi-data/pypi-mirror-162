"""Setup configuration. Nothing here, refer to setup.cfg file."""
import setuptools

import versioneer

setuptools.setup(
    version=versioneer.get_versions(),
    cmdclass=versioneer.get_cmdclass(),
)
