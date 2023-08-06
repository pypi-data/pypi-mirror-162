#
# Python3 script for defining abstract class for PPKS key managers.
# By TB Yan
# Last updated: 2021/12/27
#

from abc import ABC, abstractmethod

class AbstractPPKSKeyManager(ABC):
    @abstractmethod
    def get_configstr(self):
        raise NotImplementedError()

    @abstractmethod
    def add_pubkey(self, pubkey_pem, name):
        raise NotImplementedError()

    @abstractmethod
    def add_privkey(self, privkey_pem, name):
        raise NotImplementedError()

    @abstractmethod
    def remove_pubkey(self, indx):
        raise NotImplementedError()

    @abstractmethod
    def remove_privkey(self, indx):
        raise NotImplementedError()

    @abstractmethod
    def get_pubkey_list(self):
        raise NotImplementedError()

    @abstractmethod
    def get_pubkey(self, indx):
        raise NotImplementedError()

    @abstractmethod
    def get_privkey_list(self):
        raise NotImplementedError()

    @abstractmethod
    def get_privkey(self, indx):
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        raise NotImplementedError()

    @classmethod # We have default implementation for print names
    def get_print_name(cls):
        return cls.__name__

    @classmethod # We have default implementation for configstr names
    def get_configstr_name(cls):
        return "{}{}".format(cls.__name__, "ConfigStr")

    @classmethod
    @abstractmethod
    def prompt(cls):
        raise NotImplementedError()