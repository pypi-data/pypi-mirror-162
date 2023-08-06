#
# Python3 script for the ppksman commandline tool show subcmd.
# The show subcmd allows showing information regarding
# PPKS keys, CSRs and certificates, whether external or stored by submanagers.
# *PPKS: PPKS Public Key System, or PacketLab Public Key System
# By TB Yan
# Last updated: 2022/02/24
#

from cryptography.x509 import \
    Version, load_pem_x509_csr, load_pem_x509_certificate
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives.serialization import \
    Encoding, PublicFormat, PrivateFormat, NoEncryption
from cryptography.x509.oid import SignatureAlgorithmOID
from datetime import timezone

from ..ppks._utils import \
    is_index, multihex_fmt, \
    warn, try_get_extension, \
    safe_decode, safe_parse_digests, sha256, \
    load_key_ppksman, load_key_file, \
    load_csr_file, is_cert_valid, is_end_cert, \
    is_good_del_type, del_type_fmt, \
    KEY_SUBCMD_SET, CSR_SUBCMD_SET, CERT_SUBCMD_SET
from ..ppks.extensions import pktlab_ext_get_bytes
from ..ppks.PacketLabConstants import PacketLabConstants as pconst

#
# INTERNAL FUNCTIONS
#

def _show_key(ppksman, key_target):
    if is_index(key_target):
        pubkey, privkey = load_key_ppksman(ppksman, int(key_target))
    else:
        pubkey, privkey = load_key_file(key_target)

    prefix = ""
    if privkey is not None: # todo: give encrypted private key instead?
        print("Raw privkey:{}".format(
            multihex_fmt(
                [privkey.private_bytes(
                    Encoding.Raw, PrivateFormat.Raw, NoEncryption()).hex()])))
        print("Unencrypted privkey PEM:")
        print(privkey.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode(), end="")
        print("")
        prefix = "Corresponding "

    if pubkey is not None:
        print("{}Raw pubkey:{}".format(
            prefix,
            multihex_fmt(
                [pubkey.public_bytes(
                    Encoding.Raw, PublicFormat.Raw).hex()])))
        print("{}pubkey PEM:".format(prefix))
        print(pubkey.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode(), end="")
    return

def _load_csr_ppksman(ppksman, indx):
    return load_pem_x509_csr(ppksman.get_past_csr(indx).encode())

def _is_bad_name(name):
    name_attr_ls = name.get_attributes_for_oid(NameOID.COMMON_NAME)

    if len(name.rdns) != 1 or \
       len(name_attr_ls) != 1 or \
       name_attr_ls[0].value != "":
        return True
    return False

def _print_csr_content(csr):
    """
    For now we only perform a crude check here.
    todo: check the content constraint exactly
    """

    print("Certificate signing request (CSR) content:")

    if csr.signature_algorithm_oid != SignatureAlgorithmOID.ED25519:
        warn("CSR is NOT using Ed25519")
    if _is_bad_name(csr.subject):
        warn("CSR has BAD subject")

    print("pubkey:{}".format(
        multihex_fmt(
            [csr.public_key().public_bytes(
                Encoding.Raw, PublicFormat.Raw).hex()])))

    csr_exts = csr.extensions

    cert_type_ext = try_get_extension(pconst.PKTLAB_EXT_CERT_TYPE, csr_exts)
    if cert_type_ext is None:
        warn("NO pktlab certificate type found in CSR")
    else:
        if not cert_type_ext.critical:
            warn("CSR pktlab certificate type NOT marked critical")
        print("pktlab certificate type: {}".format(
            safe_decode(pktlab_ext_get_bytes(cert_type_ext))))

    bc_ext = try_get_extension(ExtensionOID.BASIC_CONSTRAINTS.dotted_string, csr_exts)
    if bc_ext is not None:
        if not bc_ext.critical:
            warn("CSR basic constraints NOT marked critical")
        if bc_ext.value.path_length is None:
            print("No pathlen restriction")
        else:
            print("Pathlen restriction (allowed further delegation count): {}".format(
                bc_ext.value.path_length))

    cert_desc_ext = try_get_extension(pconst.PKTLAB_EXT_CERT_DESCRIPTION, csr_exts)
    if cert_desc_ext is not None:
        if not cert_desc_ext.critical:
            warn("CSR certificate description NOT marked critical")
        print("Certificate description: '{}'".format(
            safe_decode(pktlab_ext_get_bytes(cert_desc_ext))))

    filter_digests_ext = try_get_extension(pconst.PKTLAB_EXT_FILTER_DIGESTS, csr_exts)
    if filter_digests_ext is not None:
        if not filter_digests_ext.critical:
            warn("CSR filter digests NOT marked critical")
        print("Filter digests:{}".format(
            multihex_fmt(
                safe_parse_digests(
                    pktlab_ext_get_bytes(filter_digests_ext)))))

    monitor_digests_ext = try_get_extension(pconst.PKTLAB_EXT_MONITOR_DIGESTS, csr_exts)
    if monitor_digests_ext is not None:
        if not monitor_digests_ext.critical:
            warn("CSR monitor digests NOT marked critical")
        print("Monitor digests:{}".format(
            multihex_fmt(
                safe_parse_digests(
                    pktlab_ext_get_bytes(monitor_digests_ext)))))

    priority_ext = try_get_extension(pconst.PKTLAB_EXT_PRIORITY, csr_exts)
    if priority_ext is not None:
        if not priority_ext.critical:
            warn("CSR priority NOT marked critical")
        print("Priority: '{}'".format(
            safe_decode(pktlab_ext_get_bytes(priority_ext))))

    del_type_ext = try_get_extension(pconst.PKTLAB_EXT_DEL_TYPE, csr_exts)
    if del_type_ext is not None:
        if not del_type_ext.critical:
            warn("CSR delegation type NOT marked critical")

        del_type = pktlab_ext_get_bytes(del_type_ext)
        if del_type is None or not is_good_del_type(del_type):
            warn("CSR bad delegation type field")
        else:
            print("Delegation type: {}{}".format(
                del_type, del_type_fmt(del_type)))

    print("Signature ({}):{}".format(
        "valid" if csr.is_signature_valid else "INVALID",
        multihex_fmt([csr.signature.hex()])))
    return

def _show_csr(ppksman, csr_target):
    if is_index(csr_target):
        csr = _load_csr_ppksman(ppksman, int(csr_target))
    else:
        csr = load_csr_file(csr_target)

    _print_csr_content(csr)
    print("\nCertificate signing request PEM:")
    print(csr.public_bytes(Encoding.PEM).decode(), end="")
    return

def _load_cert_ppksman(ppksman, indx):
    return load_pem_x509_certificate(ppksman.get_past_cert(indx).encode())

def _load_cert_file(path):
    with open(path, "rb") as fp:
        data = fp.read()
    return load_pem_x509_certificate(data)

def _print_cert_content(cert, supposed_aid, signature_valid=0):
    """
    For now we only perform a crude check here.
    The real check is done in the C library (should be incorporated later).
    """

    print("Certificate content:")

    if cert.version != Version.v3:
        warn("Certificate is NOT v3")
    if cert.signature_algorithm_oid != SignatureAlgorithmOID.ED25519:
        warn("Certificate is NOT using Ed25519")
    if _is_bad_name(cert.issuer):
        warn("Certificate has BAD issuer")
    if _is_bad_name(cert.subject):
        warn("Certificate has BAD subject")

    print("Serial number: {}".format(cert.serial_number))
    print("pubkey:{}".format(
        multihex_fmt(
            [cert.public_key().public_bytes(
                Encoding.Raw, PublicFormat.Raw).hex()])))
    print("Not valid before: {} (Epoch time: {})".format(
        cert.not_valid_before,
        int(cert.not_valid_before.replace(tzinfo=timezone.utc).timestamp())))
    print("Not valid after:  {} (Epoch time: {})".format(
        cert.not_valid_after,
        int(cert.not_valid_after.replace(tzinfo=timezone.utc).timestamp())))

    cert_exts = cert.extensions

    cert_type_ext = try_get_extension(pconst.PKTLAB_EXT_CERT_TYPE, cert_exts)
    if cert_type_ext is None:
        warn("NO pktlab certificate type found in certificate")
    else:
        if not cert_type_ext.critical:
            warn("Certificate pktlab certificate type NOT marked critical")
        print("pktlab certificate type: {}".format(
            safe_decode(pktlab_ext_get_bytes(cert_type_ext))))

    bc_ext = try_get_extension(ExtensionOID.BASIC_CONSTRAINTS.dotted_string, cert_exts)
    if bc_ext is None:
        warn("NO basic constraints extension found in certificate")
    else:
        if not bc_ext.critical:
            warn("Certificate basic constraints NOT marked critical")
        if not is_end_cert(safe_decode(pktlab_ext_get_bytes(cert_type_ext))): # may print trash when bad cert_type_ext
            if bc_ext.value.path_length is None:
                print("No pathlen restriction")
            else:
                print("Pathlen restriction (allowed further delegation count): {}".format(
                    bc_ext.value.path_length))

    ku_ext = try_get_extension(ExtensionOID.KEY_USAGE.dotted_string, cert_exts)
    if ku_ext is None:
        warn("NO key usage extension found in certificate")
    else:
        # only check criticality
        if not ku_ext.critical:
            warn("Certificate key usage NOT marked critical")

    aid_ext = try_get_extension(ExtensionOID.AUTHORITY_KEY_IDENTIFIER.dotted_string, cert_exts)
    if aid_ext is None:
        warn("NO authority key identifier found in certificate")
    else:
        if aid_ext.critical:
            warn("Certificate authority key identifier marked critical when should not")
        if supposed_aid is not None and \
           aid_ext.value.key_identifier != supposed_aid:
            warn("Certificate authority key identifier NOT matching signer pubkey")
        print("Authority key identifier:{}".format(
            multihex_fmt([aid_ext.value.key_identifier.hex()])))

    sid_ext = try_get_extension(ExtensionOID.SUBJECT_KEY_IDENTIFIER.dotted_string, cert_exts)
    if sid_ext is None:
        warn("NO subject key identifier found in certificate")
    else:
        if sid_ext.critical:
            warn("Certificate subject key identifier marked critical when should not")
        print("Subject key identifier:{}".format(
            multihex_fmt([sid_ext.value.digest.hex()])))

    cert_desc_ext = try_get_extension(pconst.PKTLAB_EXT_CERT_DESCRIPTION, cert_exts)
    if cert_desc_ext is not None:
        if cert_desc_ext.critical:
            warn("Certificate certificate description marked critical when should not")
        print("Certificate description: '{}'".format(
            safe_decode(pktlab_ext_get_bytes(cert_desc_ext))))

    filter_digests_ext = try_get_extension(pconst.PKTLAB_EXT_FILTER_DIGESTS, cert_exts)
    if filter_digests_ext is not None:
        if filter_digests_ext.critical:
            warn("Certificate filter digests marked critical when should not")
        print("Filter digests:{}".format(
            multihex_fmt(safe_parse_digests(
                pktlab_ext_get_bytes(filter_digests_ext)))))

    monitor_digests_ext = try_get_extension(pconst.PKTLAB_EXT_MONITOR_DIGESTS, cert_exts)
    if monitor_digests_ext is not None:
        if monitor_digests_ext.critical:
            warn("Certificate monitor digests marked critical when should not")
        print("Monitor digests:{}".format(
            multihex_fmt(safe_parse_digests(
                pktlab_ext_get_bytes(monitor_digests_ext)))))

    priority_ext = try_get_extension(pconst.PKTLAB_EXT_PRIORITY, cert_exts)
    if priority_ext is not None:
        if priority_ext.critical:
            warn("Certificate priority marked critical when should not")
        print("Priority: '{}'".format(
            safe_decode(pktlab_ext_get_bytes(priority_ext))))

    del_type_ext = try_get_extension(pconst.PKTLAB_EXT_DEL_TYPE, cert_exts)
    if del_type_ext is not None:
        if del_type_ext.critical:
            warn("Certificate delegation type marked critical when should not")

        del_type = pktlab_ext_get_bytes(del_type_ext)
        if del_type is None or not is_good_del_type(del_type):
            warn("Certificate bad delegation type")
        else:
            print("Delegation type: {}{}".format(
                del_type, del_type_fmt(del_type)))

    if signature_valid == 0:
        validity_str = "UNCHECKED"
    elif signature_valid == 1:
        validity_str = "valid"
    else:
        validity_str = "INVALID"

    print("Signature ({}):{}".format(
        validity_str, multihex_fmt([cert.signature.hex()])))
    return

def _show_cert(ppksman, cert_target, signer_pubkey_target):
    if is_index(cert_target):
        cert = _load_cert_ppksman(ppksman, int(cert_target))
    else:
        cert = _load_cert_file(cert_target)

    if signer_pubkey_target is None:
        signer_pubkey = None
    elif is_index(signer_pubkey_target):
        signer_pubkey, _ = load_key_ppksman(ppksman, int(signer_pubkey_target))
    else:
        signer_pubkey, _ = load_key_file(signer_pubkey_target)

    signature_valid = 0
    if signer_pubkey is not None:
        signature_valid = 2
        if is_cert_valid(cert, signer_pubkey):
            signature_valid = 1
    _print_cert_content(
        cert=cert,
        supposed_aid= \
            None if signer_pubkey is None \
                 else sha256(signer_pubkey.public_bytes(Encoding.Raw, PublicFormat.Raw)),
        signature_valid=signature_valid)

    print("\nCertificate PEM:")
    print(cert.public_bytes(Encoding.PEM).decode(), end="")
    return

def _update_argparse_show_key(subparsers_show):
    parser_show_key = subparsers_show.add_parser(
        "Key", aliases=["key", "k"],
        help="PPKS Manager show key subcommand")
    parser_show_key.add_argument(
        "key_target", type=str,
        help='Index to show specific key in list, or path to show specific key file')
    return

def _update_argparse_show_csr(subparsers_show):
    parser_show_csr = subparsers_show.add_parser(
        "CertificateSigningRequest", aliases=["CSR", "csr"],
        help="PPKS Manager show certificate signing request subcommand")
    parser_show_csr.add_argument(
        "csr_target", type=str,
        help=
            'Index to show specific certificate signing request in list,'+
            ' or path to show specific certificate signing request file')
    return

def _update_argparse_show_cert(subparsers_show):
    parser_show_cert = subparsers_show.add_parser(
        "Certificate", aliases=["certificate", "cert"],
        help="PPKS Manager show certificate subcommand")
    parser_show_cert.add_argument(
        "cert_target", type=str,
        help=
            'Index to show specific certificate in list,'+
            ' or path to show specific certificate file')
    parser_show_cert.add_argument(
        "-k", "--signer_pubkey", type=str,
        help=
            'Index to signer pubkey in list,'+
            ' or path to signer pubkey file')
    return

#
# EXPORTED FUNCTIONS
#

def is_show_subcmd(PPKSMan_subcommand):
    subcmd_set = {"show", "s"}
    if PPKSMan_subcommand.lower() in subcmd_set:
        return True
    return False

def update_argparse_show(subparsers_ppksman):
    parser_show = subparsers_ppksman.add_parser(
        "Show", aliases=["show", "s"],
        help="PPKS Manager show subcommand")
    subparsers_show = parser_show.add_subparsers(
        required=True, dest="PPKSMan_show_subcommand")

    _update_argparse_show_key(subparsers_show)
    _update_argparse_show_csr(subparsers_show)
    _update_argparse_show_cert(subparsers_show)
    return

def subcmd_show(ppksman, args):
    if args.PPKSMan_show_subcommand.lower() in KEY_SUBCMD_SET:
        _show_key(ppksman, args.key_target)
    elif args.PPKSMan_show_subcommand.lower() in CSR_SUBCMD_SET:
        _show_csr(ppksman, args.csr_target)
    elif args.PPKSMan_show_subcommand.lower() in CERT_SUBCMD_SET:
        _show_cert(ppksman, args.cert_target, args.signer_pubkey)
    else:
        raise ValueError(
            "Unknown show subcommand: {}".format(
                args.PPKSMan_show_subcommand))