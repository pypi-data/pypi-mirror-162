"""Services module, currently only home to SQL/persistence init method"""
import os

from ntclient import NUTRA_HOME
from ntclient.ntsqlite.sql import build_ntsqlite
from ntclient.persistence.sql.nt import nt_init
from ntclient.persistence.sql.usda import usda_init

# TODO: rethink the above imports, if this belongs in __init__ or not


def init(yes: bool = False) -> tuple:
    """
    Main init method for downloading USDA and creating NT databases.
    TODO:   Check for:
        1. .nutra folder
        2. usda
        3a. nt
        3b. default profile?
        4. prefs.json

    @param yes: bool (Skip prompting for [Y/n] in stdin)
    @return: tuple[int, bool]
    """

    print("Nutra directory  ", end="")
    if not os.path.isdir(NUTRA_HOME):
        os.makedirs(NUTRA_HOME, 0o755)
    print("..DONE!")

    # TODO: print off checks, return False if failed
    print("USDA db          ", end="")
    usda_init(yes=yes)
    print("..DONE!")

    print("Nutra db         ", end="")
    build_ntsqlite()
    nt_init()

    print("\nAll checks have passed!")
    print(
        """
Nutrient tracker is free software. It comes with NO warranty or guarantee.
You may use it as you please.
You may make changes, as long as you disclose and publish them.
    """
    )
    return 0, True
