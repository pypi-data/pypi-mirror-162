#
# Python3 script for PPKS key managers using local file system.
# Does not support concurrency yet
# By TB Yan
# Last updated: 2021/12/31
#

# todo: fix error handling

import json
import os

from .AbstractPPKSKeyManager import AbstractPPKSKeyManager
from cryptography.hazmat.primitives.asymmetric.ed25519 import \
    Ed25519PublicKey, Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

DEFAULT_DIRPATH = os.path.join(os.path.expanduser("~"), ".pktlab/keys/")

class LocalFSPPKSKeyManager(AbstractPPKSKeyManager):
    def __init__(self, configstr=None, dirpath=DEFAULT_DIRPATH):
        if configstr is None:
            # No config passed, consider to be first run
            configstr = self._init_configstr(os.path.abspath(dirpath))

        self.config = json.loads(configstr)
        if self.config["name"] != type(self).__name__:
            raise ValueError("Invalid configstr passed")

        self.special_names = {}
        self._check_setup()
        self.load_key()
        return

    def _init_configstr(self, dirpath):
        if dirpath is None:
            raise ValueError("Both config and dirpath not provided")

        config = {"name": type(self).__name__, "dirpath": dirpath}
        return json.dumps(config)

    def _dump_str(self, string, path):
        oldmask = os.umask(0o77) # only user has permission
        with open(path, "w") as fp:
            fp.write(string)
        os.umask(oldmask) # restore
        return

    def _is_no_go_priv(self, path):
        stat = os.stat(path)
        if (stat.st_mode & 0o77) != 0:
            return False
        return True

    def _check_setup(self):
        # Check directory
        if not os.path.exists(self.config["dirpath"]):
            os.makedirs(self.config["dirpath"], mode=0o700, exist_ok=True)

        if not os.path.isdir(self.config["dirpath"]):
            raise ValueError("Config parameter 'dirpath' does not point to a directory")
        return

    def _get_keyfile_ls(self, dirpath):
        # Note that we also ignore keys with overly permissive privileges
        return [i for i in os.listdir(dirpath)
                    if os.path.isfile(os.path.join(dirpath, i)) and \
                       i[0] != "." and \
                       i not in self.special_names and \
                       self._is_no_go_priv(os.path.join(dirpath, i))]

    def _try_load_ed25519_pubkey(self, pubkey_bytes):
        try:
            pubkey = serialization.load_pem_public_key(pubkey_bytes)
            if not isinstance(pubkey, Ed25519PublicKey):
                return None
            return pubkey
        except Exception:
            return None

    def _try_load_ed25519_pubkey_file(self, path):
        with open(path, "rb") as fp:
            return self._try_load_ed25519_pubkey(fp.read())

    def _is_loadable_privkey(self, privkey_bytes):
        try:
            privkey = serialization.load_pem_private_key(privkey_bytes, None)
            if not isinstance(privkey, Ed25519PrivateKey):
                return False
            return True
        except TypeError:
            return True # cannot tell key type for encrypted keys
        except Exception:
            return False

    def _is_loadable_privkey_file(self, path):
        with open(path, "rb") as fp:
            return self._is_loadable_privkey(fp.read())

    def _load_key(self):
        # For all reg files (none reg files are always ignored):
        #   1. If they start with "." or are in special names, they are ignored.
        #   2. If they end with ".pub" they are pubkeys.
        #   3. Otherwise, they are privkeys.
        #
        # pubkey files are always loaded into a dict.
        # For privkey we just store the filenames in a set.

        keyfile_ls = self._get_keyfile_ls(self.config["dirpath"])
        pubkey_dict = {}
        privkey_set = set()

        for file in keyfile_ls:
            keypath = os.path.join(self.config["dirpath"], file)

            if file[-4:] == ".pub":
                pubkey = self._try_load_ed25519_pubkey_file(keypath)
                if pubkey is not None:
                    pubkey_dict[file] = pubkey
                continue

            if self._is_loadable_privkey_file(keypath):
                privkey_set.add(file)

        return pubkey_dict, privkey_set

    def load_key(self):
        # For (re)loading keys into manager
        self.pubkey_dict, self.privkey_set = self._load_key()
        return

    def get_configstr(self):
        return json.dumps(self.config)

    def add_pubkey(self, pubkey_str, name):
        if name in self.special_names:
            raise ValueError("pubkey name cannot be {}".format(name))
        elif name[-4:] != ".pub":
            raise ValueError("pubkey name must end in '.pub'")
        elif self._try_load_ed25519_pubkey(pubkey_str.encode()) is None:
            raise ValueError("Bad pubkey")

        self._dump_str(
            pubkey_str,
            os.path.join(self.config["dirpath"], name))
        self.load_key()
        return

    def add_privkey(self, privkey_str, name):
        if name in self.special_names:
            raise ValueError("privkey name cannot be {}".format(name))
        elif name[-4:] == ".pub":
            raise ValueError("privkey name must not end in '.pub'")
        elif not self._is_loadable_privkey(privkey_str.encode()):
            raise ValueError("Bad privkey")

        self._dump_str(
            privkey_str,
            os.path.join(self.config["dirpath"], name))
        self.load_key()
        return

    def remove_pubkey(self, indx):
        name = self.get_pubkey_list()[indx]
        os.remove(os.path.join(self.config["dirpath"], name))
        self.load_key()
        return

    def remove_privkey(self, indx):
        name = self.get_privkey_list()[indx]
        os.remove(os.path.join(self.config["dirpath"], name))
        self.load_key()
        return

    def get_pubkey_list(self):
        return sorted(self.pubkey_dict.keys())

    def get_pubkey(self, indx):
        return self.pubkey_dict[self.get_pubkey_list()[indx]]

    def get_privkey_list(self):
        return sorted(self.privkey_set)

    def get_privkey(self, indx, passphrase=None):
        target = sorted(self.privkey_set)[indx]
        with open(os.path.join(self.config["dirpath"], target), "rb") as fp:
            data = fp.read()

        try:
            return serialization.load_pem_private_key(data, passphrase)
        except TypeError:
            # passphrase should be given but was not or vice versa
            # Return none for this
            pass
        return None

    def close(self): return

    @classmethod
    def prompt(cls):
        print("Initializing {}".format(cls.__name__))
        dirpath = input("Enter path to {} directory (press enter to use default path: {}): ".format(
            cls.__name__, DEFAULT_DIRPATH))

        if len(dirpath) == 0:
            return cls()
        return cls(dirpath=os.path.expanduser(dirpath))