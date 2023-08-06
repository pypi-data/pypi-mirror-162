#!/usr/bin/python3
#
# Python3 script for PPKS certificate and key manager.
# *PPKS: PPKS Public Key System, or PacketLab Public Key System
# By TB Yan
# Last updated: 2022/05/17
#

import time
from datetime import datetime

from cryptography.x509 import \
    SubjectKeyIdentifier, KeyUsage, BasicConstraints, \
    CertificateSigningRequestBuilder, Name, NameAttribute, \
    CertificateBuilder, AuthorityKeyIdentifier
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.serialization import \
    Encoding, PublicFormat, PrivateFormat, \
    NoEncryption, BestAvailableEncryption
from cryptography.hazmat.primitives.asymmetric.ed25519 import \
    Ed25519PrivateKey

from ._utils import sha256, get_raw_pubkey, is_end_cert
from .extensions import \
    PacketLabCertificateDescription, \
    PacketLabCertType, PacketLabFilterDigests, \
    PacketLabMonitorDigests, PacketLabPriority, \
    PacketLabDelegationType
from .PacketLabConstants import PacketLabConstants as pconst

#
# EXPORTED CLASSES
#

class PPKSManager:
    def __init__(self, key_manager, state_manager):
        self.key_manager = key_manager
        self.state_manager = state_manager

    def _is_valid_none(self, target, check_type):
        if check_type == -1:
            return target is None
        elif check_type == 1:
            return target is not None
        return True

    def _check_valid_opt_gen_input(
            self, except_str, cert_type,
            pathlen=None, cert_desp=None,
            monitor_digests=None, filter_digests=None,
            priority=None, del_type=None):

        """
        For raising exceptions when gen optional input invalid.
        Note cert_type is always required during gen, but is also checked here.
        """

        # -1 means should be None, 1 means should be not None, 0 means either works
        # (pathlen, cert_desp, monitor_digests, filter_digests, priority, del_type)
        cert_type_dict = {
            pconst.PKTLAB_CERTTYPE_STR_SUBCMD:  (-1, 0, -1, -1, -1, -1),
            pconst.PKTLAB_CERTTYPE_STR_PUBCMD:  (-1, 0, -1, -1,  0, -1),
            pconst.PKTLAB_CERTTYPE_STR_EXPPRIV: ( 0, 0,  0,  0,  0, -1),
            pconst.PKTLAB_CERTTYPE_STR_DELPRIV: ( 0, 0,  0,  0,  0,  1),
            pconst.PKTLAB_CERTTYPE_STR_AGENT:   (-1, 0, -1, -1, -1, -1)}
        field_name_ls = [
            "pathlen", "cert_desp",
            "monitor_digests", "filter_digests",
            "priority", "del_type"]
        input_ls = [
            pathlen, cert_desp,
            monitor_digests, filter_digests,
            priority, del_type]

        for ct in cert_type_dict:
            if ct != cert_type:
                continue

            for indx, target in enumerate(input_ls):
                if not self._is_valid_none(target, cert_type_dict[ct][indx]):
                    raise ValueError(
                        except_str.format(
                            ct,
                            "field value should be supplied but wasn't or vice versa: {}".format(
                                field_name_ls[indx])))
            break
        else:
            # got bad cert_type
            raise ValueError(except_str.format("unknown", "Bad cert_type"))

        return

    def _check_valid_opt_gen_csr_input(
            self, cert_type,
            pathlen=None, cert_desp=None,
            monitor_digests=None, filter_digests=None,
            priority=None, del_type=None):

        """
        For raising exceptions when gen CSR optional input invalid.
        Note that most optional checks are the same for cert gen as for CSR gen, as we require that:
        1. Those fields that MUST NOT appear in cert MUST NOT be provided in CSR
        2. Those fields that MUST appear in cert MUST be provided in CSR
            (as a suggestion to the signer on what to put, though the signer is free to ignore them)
        3. Those fields that can either appear or not in cert is also optional in CSR
            (also as a suggestion to the signer on what to put)
        """

        except_str = "Invalid input for generating {} CSR ({})"

        self._check_valid_opt_gen_input(
            except_str=except_str,
            cert_type=cert_type,
            pathlen=pathlen,
            cert_desp=cert_desp,
            monitor_digests=monitor_digests,
            filter_digests=filter_digests,
            priority=priority,
            del_type=del_type)
        return

    def _check_valid_opt_gen_cert_input(
            self, cert_type,
            pathlen=None, cert_desp=None,
            monitor_digests=None, filter_digests=None,
            priority=None, del_type=None):

        except_str = "Invalid input for generating {} certificate ({})"

        self._check_valid_opt_gen_input(
            except_str=except_str,
            cert_type=cert_type,
            pathlen=pathlen,
            cert_desp=cert_desp,
            monitor_digests=monitor_digests,
            filter_digests=filter_digests,
            priority=priority,
            del_type=del_type)
        return

    def _get_keyusage(self, cert_type):
        cert_sign_keyusage_tup = (
            KeyUsage(
                digital_signature=False,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False),
            True)

        end_keyusage_tup = (
            KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False),
            True)

        return end_keyusage_tup \
            if is_end_cert(cert_type) \
            else cert_sign_keyusage_tup

    def _get_basic_constraint(self, cert_type, pathlen):
        ca_basic_constraint_tup = (
            BasicConstraints(ca=True, path_length=pathlen),
            True)

        end_basic_constraint_tup = (
            BasicConstraints(ca=False, path_length=None),
            True)

        return end_basic_constraint_tup \
            if is_end_cert(cert_type) \
            else ca_basic_constraint_tup

    def _gen_cert(
            self, cert_type,
            signer_privkey, signee_pubkey,
            serialno, start_time, end_time,
            pathlen=None, cert_desp=None,
            monitor_digests=None, filter_digests=None,
            priority=None, del_type=None):

        # Note start_time and end_time should be in UTC!

        # Check optional input provision is valid (only None or not)
        # Note fields not defaulting to None (e.g. signer_privkey, time ...) are NOT checked here,
        # they are checked automatically when they are used
        # (except cert_type, which is checked here as well).
        self._check_valid_opt_gen_cert_input(
            cert_type=cert_type,
            pathlen=pathlen,
            cert_desp=cert_desp,
            monitor_digests=monitor_digests,
            filter_digests=filter_digests,
            priority=priority,
            del_type=del_type)

        # constants.values used afterwards
        empty_common_name = Name([NameAttribute(NameOID.COMMON_NAME, "")])

        # actual certificate building start here
        cert_builder = CertificateBuilder()

        # tbsCertificate contents
        # serial number
        cert_builder = cert_builder.serial_number(serialno)

        # names
        cert_builder = cert_builder.issuer_name(empty_common_name)
        cert_builder = cert_builder.subject_name(empty_common_name)

        # subject public key
        cert_builder = cert_builder.public_key(signee_pubkey)

        # valid period
        cert_builder = cert_builder.not_valid_before(
            datetime.utcfromtimestamp(start_time))
        cert_builder = cert_builder.not_valid_after(
            datetime.utcfromtimestamp(end_time))

        # extensions
        ext_tup_ls = []

        # AID
        AID_tup = (
            AuthorityKeyIdentifier(
                sha256(get_raw_pubkey(signer_privkey.public_key())),
                None, None),
            False)
        ext_tup_ls.append(AID_tup)

        # SID
        SID_tup = (
            SubjectKeyIdentifier(
                sha256(get_raw_pubkey(signee_pubkey))),
            False)
        ext_tup_ls.append(SID_tup)

        # KeyUsage
        keyusage_tup = self._get_keyusage(cert_type)
        ext_tup_ls.append(keyusage_tup)

        # BasicConstraint
        basic_constraint_tup = self._get_basic_constraint(cert_type, pathlen)
        ext_tup_ls.append(basic_constraint_tup)

        # pktlab custom extensions
        # certificate type
        cert_type_tup = (
            PacketLabCertType(cert_type), True)
        ext_tup_ls.append(cert_type_tup)

        # certificate description
        if cert_desp is not None:
            cert_description_tup = (
                PacketLabCertificateDescription(cert_desp), False)
            ext_tup_ls.append(cert_description_tup)

        # filter digest list
        if filter_digests is not None:
            filter_digests_tup = (
                PacketLabFilterDigests(filter_digests), False)
            ext_tup_ls.append(filter_digests_tup)

        # monitor digest list
        if monitor_digests is not None:
            monitor_digests_tup = (
                PacketLabMonitorDigests(monitor_digests), False)
            ext_tup_ls.append(monitor_digests_tup)

        # priority
        if priority is not None:
            priority_tup = (
                PacketLabPriority(priority), False)
            ext_tup_ls.append(priority_tup)

        # del_type
        if del_type is not None:
            del_type_tup = (
                PacketLabDelegationType(del_type), False)
            ext_tup_ls.append(del_type_tup)

        for (ext, critical) in ext_tup_ls:
            cert_builder = cert_builder.add_extension(ext, critical=critical)

        cert = cert_builder.sign(signer_privkey, None)
        return cert

    def _gen_csr(
            self, cert_type,
            signee_privkey,
            pathlen=None, cert_desp=None,
            monitor_digests=None, filter_digests=None,
            priority=None, del_type=None):

        # Note start_time and end_time should be in UTC!

        # Check optional input provision is valid (only None or not)
        # Note fields not defaulting to None (e.g. signer_privkey, ...) are NOT checked here,
        # they are checked automatically when they are used (except cert_type, which is checked here).
        self._check_valid_opt_gen_csr_input(
            cert_type=cert_type,
            pathlen=pathlen,
            cert_desp=cert_desp,
            monitor_digests=monitor_digests,
            filter_digests=filter_digests,
            priority=priority,
            del_type=del_type)

        # constants.values used afterwards
        empty_common_name = Name([NameAttribute(NameOID.COMMON_NAME, "")])

        # actual certificate building start here
        csr_builder = CertificateSigningRequestBuilder()

        # CertificationRequestInfo contents
        # subject
        csr_builder = csr_builder.subject_name(empty_common_name)

        # subjectPKInfo is filled in automatically when signing CSR
        # attributes
        ext_tup_ls = []

        # BasicConstraint
        if pathlen is not None:
            basic_constraint_tup = self._get_basic_constraint(cert_type, pathlen)
            ext_tup_ls.append(basic_constraint_tup)

        # pktlab custom extensions
        # certificate type
        cert_type_tup = (
            PacketLabCertType(cert_type), True)
        ext_tup_ls.append(cert_type_tup)

        # certificate description
        if cert_desp is not None:
            cert_description_tup = (
                PacketLabCertificateDescription(cert_desp), True)
            ext_tup_ls.append(cert_description_tup)

        # filter digest list
        if filter_digests is not None:
            filter_digests_tup = (
                PacketLabFilterDigests(filter_digests), True)
            ext_tup_ls.append(filter_digests_tup)

        # monitor digest list
        if monitor_digests is not None:
            monitor_digests_tup = (
                PacketLabMonitorDigests(monitor_digests), True)
            ext_tup_ls.append(monitor_digests_tup)

        # priority
        if priority is not None:
            priority_tup = (
                PacketLabPriority(priority), True)
            ext_tup_ls.append(priority_tup)

        # del_type
        if del_type is not None:
            del_type_tup = (
                PacketLabDelegationType(del_type), True)
            ext_tup_ls.append(del_type_tup)

        for (ext, critical) in ext_tup_ls:
            csr_builder = csr_builder.add_extension(ext, critical=critical)

        csr = csr_builder.sign(signee_privkey, None)
        return csr

    def _record_signed(self, record_func, stuff, name):
        record_func(stuff, "{}.".format(int(time.time()))+name)
        return

    def gen_key(self, name, passphrase):
        if name+".pub" in self.get_pubkey_list() or \
           name in self.get_privkey_list():
            raise ValueError("Key name already exists in key lists")

        privkey = Ed25519PrivateKey.generate()
        pubkey = privkey.public_key()

        pubkey_bytes = pubkey.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo)

        if len(passphrase) == 0:
            encryption_algorithm = NoEncryption()
        else:
            encryption_algorithm = BestAvailableEncryption(passphrase)

        privkey_bytes = privkey.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm)

        self.key_manager.add_pubkey(pubkey_bytes.decode(), name+".pub")
        self.key_manager.add_privkey(privkey_bytes.decode(), name)
        return pubkey_bytes, privkey_bytes

    def import_pubkey(self, pubkey_str, name):
        if name in self.get_pubkey_list():
            raise ValueError("Key name already exists in pubkey list")
        self.key_manager.add_pubkey(pubkey_str, name)
        return

    def get_pubkey_list(self):
        return self.key_manager.get_pubkey_list()

    def get_pubkey(self, indx):
        return self.key_manager.get_pubkey(indx)

    def remove_pubkey(self, indx):
        self.key_manager.remove_pubkey(indx)
        return

    def import_privkey(self, privkey_str, name):
        if name in self.get_privkey_list():
            raise ValueError("Key name already exists in privkey list")
        self.key_manager.add_privkey(privkey_str, name)
        return

    def get_privkey_list(self):
        return self.key_manager.get_privkey_list()

    def get_privkey(self, indx, passphrase=None):
        return self.key_manager.get_privkey(indx, passphrase)

    def remove_privkey(self, indx):
        self.key_manager.remove_privkey(indx)
        return

    def gen_csr(
            self, name, cert_type,
            signee_privkey,
            pathlen=None, cert_desp=None,
            monitor_digests=None, filter_digests=None,
            priority=None, del_type=None):

        csr = self._gen_csr(
            cert_type=cert_type,
            signee_privkey=signee_privkey,
            pathlen=pathlen,
            cert_desp=cert_desp,
            monitor_digests=monitor_digests,
            filter_digests=filter_digests,
            priority=priority,
            del_type=del_type)

        # update state if successful
        if csr is not None:
            self._record_signed(
                self.state_manager.record_new_csr,
                csr.public_bytes(Encoding.PEM).decode(), name)

        return csr

    def get_past_csr_list(self):
        return self.state_manager.get_past_csr_list()

    def get_past_csr(self, indx):
        return self.state_manager.get_past_csr(indx)

    def remove_past_csr(self, indx):
        self.state_manager.remove_csr(indx)
        return

    def gen_cert(
            self, name, cert_type,
            signer_privkey, signee_pubkey,
            start_time, end_time,
            pathlen=None, cert_desp=None,
            monitor_digests=None, filter_digests=None,
            priority=None, del_type=None):

        # gen cert
        _, serialno = self.state_manager.get_serialno()
        cert = self._gen_cert(
            cert_type=cert_type,
            signer_privkey=signer_privkey,
            signee_pubkey=signee_pubkey,
            serialno=serialno,
            start_time=start_time,
            end_time=end_time,
            pathlen=pathlen,
            cert_desp=cert_desp,
            monitor_digests=monitor_digests,
            filter_digests=filter_digests,
            priority=priority,
            del_type=del_type)

        # update state if successful
        if cert is not None:
            self.state_manager.update_serial_indx()
            self._record_signed(
                self.state_manager.record_new_cert,
                cert.public_bytes(Encoding.PEM).decode(), name)

        return cert

    def get_past_cert_list(self):
        return self.state_manager.get_past_cert_list()

    def get_past_cert(self, indx):
        return self.state_manager.get_past_cert(indx)

    def remove_past_cert(self, indx):
        self.state_manager.remove_cert(indx)
        return