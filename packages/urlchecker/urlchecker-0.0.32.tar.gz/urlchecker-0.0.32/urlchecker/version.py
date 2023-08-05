"""

Copyright (c) 2020-2022 Ayoub Malek and Vanessa Sochat

This source code is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""

__version__ = "0.0.32"
AUTHOR = "Ayoub Malek, Vanessa Sochat"
AUTHOR_EMAIL = "superkogito@gmail.com, vsochat@stanford.edu"
NAME = "urlchecker"
PACKAGE_URL = "http://www.github.com/urlstechie/urlchecker-python"
KEYWORDS = "urls, static checking, checking, validation"
DESCRIPTION = (
    "tool to collect and validate urls over static files (code and documentation)"
)
LICENSE = "LICENSE"


################################################################################
# Global requirements


INSTALL_REQUIRES = (
    ("requests", {"min_version": "2.18.4"}),
    # Recommended: pip install git+https://github.com/danger89/fake-useragent.git
    ("fake-useragent", {"min_version": None}),
)

SELENIUM_REQUIRES = (("selenium", {"min_version": None}),)

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)

INSTALL_REQUIRES_ALL = INSTALL_REQUIRES + SELENIUM_REQUIRES + TESTS_REQUIRES
