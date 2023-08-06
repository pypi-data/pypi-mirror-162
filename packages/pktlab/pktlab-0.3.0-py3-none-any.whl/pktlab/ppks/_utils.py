#
# Python3 script for general utility functions and constants.
# By TB Yan
# Last updated: 2022/05/17
#

import os
import getpass

from cryptography.hazmat.primitives.hashes import Hash, SHA256
from cryptography.hazmat.primitives.serialization import \
    Encoding, PublicFormat, \
    load_pem_public_key, load_pem_private_key
from cryptography.x509 import \
    ObjectIdentifier, load_pem_x509_csr, ExtensionNotFound
from cryptography.exceptions import InvalidSignature
from math import ceil
from sys import stderr

from .LocalFSPPKSKeyManager import LocalFSPPKSKeyManager
from .LocalFSPPKSStateManager import LocalFSPPKSStateManager
from .PacketLabConstants import PacketLabConstants as pconst

#
# EXPORTED CONSTANTS
#

KEYMAN_LS = [
    LocalFSPPKSKeyManager
]
STATEMAN_LS = [
    LocalFSPPKSStateManager
]

KEY_SUBCMD_SET  = {"key", "k"}
CSR_SUBCMD_SET  = {"certificatesigningrequest", "csr"}
CERT_SUBCMD_SET = {"certificate", "cert"}

#
# UTILITY METHOD DEFINITIONS
#

def sha256(data):
    digest = Hash(SHA256())
    digest.update(data)
    return digest.finalize()

def get_raw_pubkey(pubkey):
    return pubkey.public_bytes(Encoding("Raw"), PublicFormat("Raw"))

def get_cert_type_str(cert_type):
    num2name_map = {
        pconst.PKTLAB_CERT_SUBCMD:  pconst.PKTLAB_CERTTYPE_STR_SUBCMD,
        pconst.PKTLAB_CERT_PUBCMD:  pconst.PKTLAB_CERTTYPE_STR_PUBCMD,
        pconst.PKTLAB_CERT_EXPPRIV: pconst.PKTLAB_CERTTYPE_STR_EXPPRIV,
        pconst.PKTLAB_CERT_DELPRIV: pconst.PKTLAB_CERTTYPE_STR_DELPRIV,
        pconst.PKTLAB_CERT_AGENT:   pconst.PKTLAB_CERTTYPE_STR_AGENT}

    if cert_type not in num2name_map:
        return pconst.PKTLAB_CERTTYPE_STR_UNKNOWN

    return num2name_map[cert_type]

def is_end_cert(cert_type):
    if cert_type == pconst.PKTLAB_CERT_SUBCMD or \
       cert_type == pconst.PKTLAB_CERT_PUBCMD or \
       cert_type == pconst.PKTLAB_CERT_AGENT or \
       cert_type == pconst.PKTLAB_CERTTYPE_STR_SUBCMD or \
       cert_type == pconst.PKTLAB_CERTTYPE_STR_PUBCMD or \
       cert_type == pconst.PKTLAB_CERTTYPE_STR_AGENT:
        return True
    return False

def yes_no_prompt(start_text, fail_text, default=-1):
    """
    default parameter meaning:
        -1 -> enter means no
         0 -> enter is incorrect input
         1 -> enter means yes
    """

    assert default in range(-1, 2)

    while True:
        reply = input(start_text).lower()

        if len(reply) == 0:
            if default == -1:
                return False
            elif default == 1:
                return True
            # do nothing when default == 0
        elif reply == "y" or reply == "yes":
            return True
        elif reply == "n" or reply == "no":
            return False

        print(fail_text)

def multistr_fmt(str_ls):
    return "".join(["\n\t"+i for i in str_ls])

def multihex_fmt(hex_ls):
    hex_seg = []
    for indx, h in enumerate(hex_ls):
        tmp = [h[32*i:32*i+16] + " " + h[32*i+16:32*(i+1)] for i in range(ceil(len(h)/32))]
        if indx != len(hex_ls)-1:
            tmp[-1] = tmp[-1]+","
        if indx != 0:
            hex_seg.append("")
        hex_seg += tmp
    return "".join(["\n\t"+i for i in hex_seg])

def del_type_fmt(del_type):
    del_exppriv, del_reppriv = decode_del_type(del_type)
    return \
        multistr_fmt([
            "Delegate experiment privilege: {}".format(del_exppriv),
            "Delegate represent privilege: {}".format(del_reppriv)])

def warn(string):
    print("Warning: {}".format(string), file=stderr)

def is_index(s):
    try:
        rst = int(s.strip())
    except Exception as e:
        return False

    if rst < 0:
        return False
    return True

def try_get_extension(oidstr, extensions):
    try:
        return extensions.get_extension_for_oid(ObjectIdentifier(oidstr))
    except ExtensionNotFound:
        return None

def safe_decode(b):
    return b if b is None else b.decode()

def safe_parse_digests(f):
    if f is None: return None
    all_digests = f.hex()
    digest_hex_len = pconst.PKTLAB_SHA256_DIGEST_LEN*2
    return [
        all_digests[i:i+digest_hex_len]
        for i in range(0, len(all_digests), digest_hex_len)]

def list_names(start_output, name_ls, start_indx=0):
    print(start_output)
    for i, name in enumerate(name_ls):
        print("\t{}. {}".format(i+start_indx, name))
    return

def is_cert_valid(cert, signer_pubkey):
    try:
        signer_pubkey.verify(cert.signature, cert.tbs_certificate_bytes)
        return True
    except InvalidSignature:
        return False

def is_good_del_type(dt):
    if not isinstance(dt, bytes) or \
       len(dt) != 1 or \
       (dt[0] & \
        ~pconst.PKTLAB_DEL_TYPE_EXPPRIV & \
        ~pconst.PKTLAB_DEL_TYPE_REPPRIV) != 0:
        return False
    return True

def comp_del_type(del_exppriv, del_reppriv):
    ret = 0
    if del_exppriv:
        ret |= pconst.PKTLAB_DEL_TYPE_EXPPRIV
    if del_reppriv:
        ret |= pconst.PKTLAB_DEL_TYPE_REPPRIV
    return bytes([ret]) if ret != 0 else None

def decode_del_type(del_type):
    # does not check if del type is well-formed
    return \
        del_type[0] & pconst.PKTLAB_DEL_TYPE_EXPPRIV != 0, \
        del_type[0] & pconst.PKTLAB_DEL_TYPE_REPPRIV != 0

#
# LOAD FUNCTIONS
#

def prompt_passphrase(privkey_name):
    passphrase = getpass.getpass(
        "Please enter passphrase for Ed25519 private key ({}): ".format(
            privkey_name))
    return bytes(passphrase, encoding="utf8")

def load_privkey_ppksman(ppksman, indx):
    privkey = ppksman.get_privkey(indx) # try loading without passphrase
    if privkey is not None:
        return privkey

    # prompt passphrase and load with passphrase
    passphrase = prompt_passphrase("privkey list indx: {}".format(indx))
    return ppksman.get_privkey(indx, passphrase)

def load_key_ppksman(ppksman, indx):
    pubkey_ls = ppksman.get_pubkey_list()
    if indx in range(len(pubkey_ls)):
        return ppksman.get_pubkey(indx), None

    privkey = load_privkey_ppksman(ppksman, indx-len(pubkey_ls))
    return privkey.public_key(), privkey

def load_privkey_file(path):
    with open(path, "rb") as fp:
        data = fp.read()

    try:
        privkey = load_pem_private_key(data, None)
        return privkey.public_key(), privkey # try loading without passphrase
    except TypeError:
        pass # need passphrase

    # prompt passphrase and load with passphrase
    passphrase = prompt_passphrase(path)
    privkey = load_pem_private_key(data, passphrase)
    return privkey.public_key(), privkey

def load_key_file(path):
    name = os.path.basename(os.path.abspath(path))
    if name[-4:] == ".pub":
        with open(path, "rb") as fp:
            pubkey = load_pem_public_key(fp.read())
        privkey = None
    else:
        pubkey, privkey = load_privkey_file(path)

    return pubkey, privkey

def load_csr_file(path):
    with open(path, "rb") as fp:
        data = fp.read()
    return load_pem_x509_csr(data)

def load_config(path):
    if not os.path.exists(path) or not os.path.isfile(path):
        return None, None

    with open(path, "r") as fp:
        data = fp.readlines()

    keyman_configstr_name_set = {c.get_configstr_name() for c in KEYMAN_LS}
    stateman_configstr_name_set = {c.get_configstr_name() for c in STATEMAN_LS}
    assert len(keyman_configstr_name_set.intersection(stateman_configstr_name_set)) == 0

    keyman_configstr_tup = None
    stateman_configstr_tup = None

    for line in data:
        if len(line) > 0 and line[0] == "#":
            continue # comments

        parsedline = line.strip().split(maxsplit=1)
        if len(parsedline) == 0:
            continue
        elif parsedline[0] in keyman_configstr_name_set:
            if keyman_configstr_tup is not None:
                raise ValueError("Bad config format: multiple KeyManager configstr")
            keyman_configstr_tup = (parsedline[0], parsedline[1])
        elif parsedline[0] in stateman_configstr_name_set:
            if stateman_configstr_tup is not None:
                raise ValueError("Bad config format: multiple StateManager configstr")
            stateman_configstr_tup = (parsedline[0], parsedline[1])
        else: # Bad config format
            raise ValueError(
                "Bad config format: unknown configstr name ({})".format(parsedline[0]))

    return keyman_configstr_tup, stateman_configstr_tup