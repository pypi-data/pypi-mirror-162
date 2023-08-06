#
# Python3 script for defining abstract class for PPKS state managers.
# By TB Yan
# Last updated: 2021/12/27
#

from abc import ABC, abstractmethod

class AbstractPPKSStateManager(ABC):
    @abstractmethod
    def get_configstr(self):
        raise NotImplementedError()

    @abstractmethod
    def get_serialno(self):
        raise NotImplementedError()

    @abstractmethod
    def update_serial_indx(self):
        raise NotImplementedError()

    @abstractmethod
    def record_new_csr(self, csr):
        raise NotImplementedError()

    @abstractmethod
    def remove_csr(self, indx):
        raise NotImplementedError()

    @abstractmethod
    def get_past_csr_list(self):
        raise NotImplementedError()

    @abstractmethod
    def get_past_csr(self, indx):
        raise NotImplementedError()

    @abstractmethod
    def record_new_cert(self, cert):
        raise NotImplementedError()

    @abstractmethod
    def remove_cert(self, indx):
        raise NotImplementedError()

    @abstractmethod
    def get_past_cert_list(self):
        raise NotImplementedError()

    @abstractmethod
    def get_past_cert(self, indx):
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