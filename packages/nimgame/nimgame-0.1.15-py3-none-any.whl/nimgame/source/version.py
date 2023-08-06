"""Version in a separate module

This way it can be imported and used for package building and docs

The version info and string has the following elements:

    Major version
        to increase, when something substantial changes or not backward compatible
        anymore

    Minor version
        to increase, when new (backward compatible) features are introduced

    Patches
        to fix issues
"""

# Version of the package
__version_info__ = ('0', '1', '15')
__version__ = '.'.join(__version_info__)
