
# Copyright (C) 2012-2022 james jameson





if __name__ == "__main__":

    from setuptools import setup, find_packages

    import sys

    if sys.version_info[:2] < (3, 7):
        raise RuntimeError("dbm_test123 requires python >= 3.7.")

    setup()
