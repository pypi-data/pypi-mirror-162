#
# Python3 script for PPKS state managers using local file system.
# Does NOT support concurrency (for now).
# By TB Yan
# Last updated: 2022/02/02
#

import json
import os
import shelve

from .AbstractPPKSStateManager import AbstractPPKSStateManager
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SEEDSZ = 16
DEFAULT_DIRPATH = os.path.join(os.path.expanduser("~"), ".pktlab/certs/")

class LocalFSPPKSStateManager(AbstractPPKSStateManager):
    def __init__(self, configstr=None, dirpath=DEFAULT_DIRPATH):
        if configstr is None:
            # No config passed, consider to be first run
            configstr = self._init_configstr(os.path.abspath(dirpath))

        self.config = json.loads(configstr)
        if self.config["name"] != type(self).__name__:
            raise ValueError("Invalid configstr passed")

        self.special_names = {"seed", "serialindx", "ver"}
        self._setup_dir()
        self._setup_db()
        self._setup_serial()
        return

    def _init_configstr(self, dirpath):
        if dirpath is None:
            raise ValueError("dirpath not provided")

        config = {"name": type(self).__name__, "dirpath": dirpath}
        return json.dumps(config)

    def _setup_dir(self):
        # Set up directory
        if not os.path.exists(self.config["dirpath"]):
            os.makedirs(self.config["dirpath"], mode=0o700, exist_ok=True)

        if not os.path.isdir(self.config["dirpath"]):
            raise ValueError("Config parameter 'dirpath' does not point to a directory")
        return

    def _setup_db(self):
        # Set up shelve database
        dbpath = os.path.join(self.config["dirpath"], ".db")
        if os.path.exists(dbpath) and not os.path.isfile(dbpath):
            raise ValueError("{} does not point to a regular file".format(dbpath))

        # WARNING: db (file and in memory obj) updated only when assigned!!
        # See https://docs.python.org/3/library/shelve.html#shelve.open
        oldmask = os.umask(0o77) # only user has permission
        self.db = shelve.open(dbpath, flag="c")
        os.umask(oldmask) # restore

        # set ver, in case we need to modify the db layout later
        if "ver" not in self.db:
            self.db["ver"] = 0
        return

    def _setup_serial(self):
        # Set up database if not done yet
        if "seed" not in self.db:
            self.db["seed"] = self._gen_seed()
        if "serialindx" not in self.db:
            self.db["serialindx"] = 0
        return

    def _gen_seed(self):
        return os.urandom(SEEDSZ) # in bytes

    def _record_stuff(self, stuff, name, is_cert):
        if name in self.db:
            raise KeyError(
                "Name '{}' already exists in manager db".format(name))
        self.db[name] = (stuff, is_cert) # False means is not certificate
        return

    def _get_stuff_list(self, is_cert):
        return sorted([
            k for k in self.db
                if k not in self.special_names and
                   self.db[k][1] == is_cert])

    def get_configstr(self):
        return json.dumps(self.config)

    def get_serialno(self):
        serialindx = self.db["serialindx"]
        if serialindx >= 2**128 or serialindx < 0:
            raise ValueError("serialindx out of range")
        return \
            serialindx, \
            int.from_bytes(
                AES_encrypt(
                    self.db["seed"],
                    serialindx.to_bytes(16, byteorder='big')),
                byteorder="big")

    def update_serial_indx(self):
        self.db["serialindx"] = self.db["serialindx"]+1
        return

    def record_new_csr(self, csr, name):
        if not isinstance(csr, str):
            raise ValueError("Provided CSR in bad type: {}".format(type(csr)))

        self._record_stuff(csr, name, False)
        return

    def remove_csr(self, indx):
        del self.db[self.get_past_csr_list()[indx]]
        return

    def get_past_csr_list(self):
        return self._get_stuff_list(False)

    def get_past_csr(self, indx):
        return self.db[self.get_past_csr_list()[indx]][0]

    def record_new_cert(self, cert, name):
        if not isinstance(cert, str):
            raise ValueError("Provided certificate in bad type: {}".format(type(cert)))

        self._record_stuff(cert, name, True)
        return

    def remove_cert(self, indx):
        del self.db[self.get_past_cert_list()[indx]]
        return

    def get_past_cert_list(self):
        return self._get_stuff_list(True)

    def get_past_cert(self, indx):
        return self.db[self.get_past_cert_list()[indx]][0]

    def close(self):
        self.db.close()
        self.db = None
        return

    @classmethod
    def prompt(cls):
        print("Initializing {}".format(cls.__name__))
        dirpath = input("Enter path to {} directory (press enter to use default path: {}): ".format(
            cls.__name__, DEFAULT_DIRPATH))

        if len(dirpath) == 0:
            return cls()
        return cls(dirpath=os.path.expanduser(dirpath))

def AES_encrypt(key, data):
    if len(key) != 16 or len(data) != 16:
        raise ValueError(
            "Bad key ({}) or data ({}): Not 128 bits long)".format(
                len(key), len(data)))
    prp = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    return prp.update(data)+prp.finalize()

def AES_decrypt(key, data):
    if len(key) != 16 or len(data) != 16:
        raise ValueError(
            "Bad key ({}) or data ({}): Not 128 bits long)".format(
                len(key), len(data)))
    prp = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
    return prp.update(data)+prp.finalize()