#
# Python3 script for the ppksman commandline tool gen subcmd.
# The gen subcmd allows generation of PPKS CSRs, certificates and keys.
# *PPKS: PPKS Public Key System, or PacketLab Public Key System
# By TB Yan
# Last updated: 2022/05/17
#

import os
from getpass import getpass

from cryptography.x509.oid import ExtensionOID
from cryptography.hazmat.primitives.serialization import \
    Encoding, PublicFormat

from ..ppks._utils import \
    is_index, warn, yes_no_prompt, \
    load_key_ppksman, load_key_file, \
    load_csr_file, try_get_extension, \
    safe_decode, safe_parse_digests, \
    multihex_fmt, comp_del_type, del_type_fmt, \
    KEY_SUBCMD_SET, CSR_SUBCMD_SET, CERT_SUBCMD_SET
from ..ppks.extensions import pktlab_ext_get_bytes
from ..ppks.PacketLabConstants import PacketLabConstants as pconst

#
# INTERNAL FUNCTIONS
#

def _prompt_new_passphrase():
    passphrase = getpass(
        "Please enter passphrase for Ed25519 private key " +
        "(press enter for no passphrase): ")

    if len(passphrase) != 0:
        passphrase_confirm = getpass("Please re-enter passphrase: ")
        if passphrase != passphrase_confirm:
            print("Passphrase does not match, aborting")
            return None

    return passphrase.encode()

def _genkey(ppksman, keyname, keypath):
    """
    keyname for storing with ppksman
    keypath for storing at additional location
    """

    passphrase = _prompt_new_passphrase()
    pubkey_bytes, privkey_bytes = ppksman.gen_key(keyname, passphrase)

    if keypath is not None:
        oldmask = os.umask(0o77) # only user has permission
        with open(keypath+".pub", "wb") as fp:
            fp.write(pubkey_bytes)
        with open(keypath, "wb") as fp:
            fp.write(privkey_bytes)
        os.umask(oldmask) # restore

    print("Key generation completed")
    return

def _fill_in_prompt_str(base_fmt, use_csr, print_content):
    return base_fmt.format(
        " (from CSR)" if use_csr == 1 else "",
        print_content)

def _get_privkey_short_desc(name, privkey):
    return "\n\tKey: {}\n\tLeading 4 bytes of corresponding public key: {}".format(
        name, privkey.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)[:4].hex())

def _get_pubkey_short_desc(name, pubkey):
    return "\n\tKey: {}\n\tLeading 4 bytes: {}".format(
        name, pubkey.public_bytes(Encoding.Raw, PublicFormat.Raw)[:4].hex())

def _prompt_input_info(
        cert_type_tup,
        signer_privkey_tup,
        signee_pubkey_tup,
        signee_privkey_tup,
        start_time_tup, end_time_tup,
        pathlen_tup, cert_desp_tup,
        monitor_digests_tup, filter_digests_tup,
        priority_tup, del_type_tup,
        signrst, ask):
    """
    Return True for can continue, return False if should terminate.
    Note that the meaning of the second value of the input tuples:
        0: value not supplied by user, i.e. should not prompt
        1: value supplied by user via CSR
        2: value supplied by user via commandline
    """

    print("--------------------------------------------------------------")
    print("Proceeding to sign {} with the following information:".format(signrst))
    print_strs = []

    if cert_type_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "Certificate type{}: {}",
                cert_type_tup[1],
                cert_type_tup[0]))

    if signer_privkey_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "Signer private key{}:{}",
                signer_privkey_tup[1],
                _get_privkey_short_desc(
                    signer_privkey_tup[2],
                    signer_privkey_tup[0])))

    if signee_pubkey_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "Signee public key{}:{}",
                signee_pubkey_tup[1],
                _get_pubkey_short_desc(
                    signee_pubkey_tup[2],
                    signee_pubkey_tup[0])))

    if signee_privkey_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "Signee private key{}:{}",
                signee_privkey_tup[1],
                _get_privkey_short_desc(
                    signee_privkey_tup[2],
                    signee_privkey_tup[0])))

    if start_time_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "Valid not before (Epoch time){}: {}",
                start_time_tup[1], start_time_tup[0]))

    if end_time_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "Valid not after (Epoch time){}:  {}",
                end_time_tup[1], end_time_tup[0]))

    if pathlen_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "Path length{}: {}",
                pathlen_tup[1], pathlen_tup[0]))

    if cert_desp_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "Certificate description{}: '{}'",
                cert_desp_tup[1], cert_desp_tup[0]))

    if monitor_digests_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "Monitor digests{}:{}",
                monitor_digests_tup[1],
                multihex_fmt(monitor_digests_tup[0])))
    if filter_digests_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "Filter digests{}:{}",
                filter_digests_tup[1],
                multihex_fmt(filter_digests_tup[0])))

    if priority_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "Priority{}: '{}'",
                priority_tup[1], priority_tup[0]))

    if del_type_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "Delegation type{}: {}",
                del_type_tup[1],
                "{}{}".format(
                    del_type_tup[0],
                    del_type_fmt(del_type_tup[0]))))

    for print_str in print_strs:
        print(print_str)
    print("--------------------------------------------------------------")

    if ask:
        return yes_no_prompt(
            start_text="Is the above information correct? (y/N) ",
            fail_text="Unrecognized input, please try again")

    return True

def _prep_data_tup(csr_data, passed_data):
    if csr_data is None and passed_data is None:
        prompt_type = 0
        data = None
    elif passed_data is not None:
        prompt_type = 2
        data = passed_data
    else:
        prompt_type = 1
        data = csr_data

    return (data, prompt_type)

def _prep_data_tup_key(csr_data, passed_data, passed_data_name):
    tup = _prep_data_tup(csr_data, passed_data)
    if csr_data is None and passed_data is None:
        return (*tup, "not supplied")
    elif passed_data is not None:
        return (*tup, passed_data_name)
    else:
        return (*tup, "from CSR")

def _fix0x(string):
    return string[2:] if string[:2] == "0x" else string

def _prep_hex_list(ls):
    if ls is None:
        return None
    return bytes.fromhex("".join([_fix0x(i) for i in ls]))

def _is_good_digest_ls(ls):
    if ls is None:
        return True
    if len(ls) == 0:
        return False
    for d in ls:
        if len(_fix0x(d)) != pconst.PKTLAB_SHA256_DIGEST_LEN*2:
            return False
    return True

def _sign_csr(
        ppksman, cert_type,
        signee_privkey,
        signee_privkey_name,
        pathlen, cert_desp,
        monitor_digests, filter_digests,
        priority, del_type,
        path, ask):

    if not _prompt_input_info(
            cert_type_tup=(cert_type, 2),
            signer_privkey_tup=(None, 0, ""),
            signee_pubkey_tup=(None, 0, ""),
            signee_privkey_tup=(signee_privkey, 2, signee_privkey_name),
            start_time_tup=(None, 0),
            end_time_tup=(None, 0),
            pathlen_tup=_prep_data_tup(None, pathlen),
            cert_desp_tup=_prep_data_tup(None, cert_desp),
            monitor_digests_tup=_prep_data_tup(None, monitor_digests),
            filter_digests_tup=_prep_data_tup(None, filter_digests),
            priority_tup=_prep_data_tup(None, priority),
            del_type_tup=_prep_data_tup(None, del_type),
            signrst="CSR",
            ask=ask):
        print("Command aborted")
        return

    if not _is_good_digest_ls(monitor_digests):
        raise ValueError("Bad monitor digest list")
    if not _is_good_digest_ls(filter_digests):
        raise ValueError("Bad filter digest list")

    csr = ppksman.gen_csr(
        name=os.path.basename(path),
        cert_type=cert_type,
        signee_privkey=signee_privkey,
        pathlen=pathlen,
        cert_desp=cert_desp,
        monitor_digests=_prep_hex_list(monitor_digests),
        filter_digests=_prep_hex_list(filter_digests),
        priority=priority,
        del_type=del_type)

    if csr is None:
        print("CSR signing failed; state is not updated")
        return

    with open(path, "w") as fp:
        fp.write(csr.public_bytes(Encoding.PEM).decode())

    print("\nSigned certificate signing request PEM:")
    print(csr.public_bytes(Encoding.PEM).decode(), end="")
    print("CSR signing succeeded")
    return csr

def _sign_cert(
        ppksman, csr, cert_type,
        signer_privkey,
        signer_privkey_name,
        signee_pubkey,
        signee_pubkey_name,
        start_time, end_time,
        pathlen, cert_desp,
        monitor_digests, filter_digests,
        priority, del_type,
        path, ask):

    if csr is not None:
        # Extract information from CSR
        # Note that if also provided via commandline, the commandline info is always preferred
        csr_exts = csr.extensions

        csr_cert_type = safe_decode(
            pktlab_ext_get_bytes(
                try_get_extension(
                    pconst.PKTLAB_EXT_CERT_TYPE, csr_exts)))
        if csr_cert_type is not None and \
           cert_type is not None and \
           csr_cert_type != cert_type:
            warn(
                "CSR certificate type ({}) does not match supplied certificate type ({})".format(
                csr_cert_type, cert_type))

        cert_type_tup       = _prep_data_tup(csr_cert_type, cert_type)
        signer_privkey_tup  = (signer_privkey, 2, signer_privkey_name)
        signee_pubkey_tup   = _prep_data_tup_key(csr.public_key(), signee_pubkey, signee_pubkey_name)
        start_time_tup      = (start_time, 2)
        end_time_tup        = (end_time, 2)
        bc                  = try_get_extension(
            ExtensionOID.BASIC_CONSTRAINTS.dotted_string, csr_exts)
        pathlen_tup         = _prep_data_tup(
            bc.value.path_length if bc is not None else None, pathlen)
        cert_desp_tup       = _prep_data_tup(
            safe_decode(
                pktlab_ext_get_bytes(
                    try_get_extension(
                        pconst.PKTLAB_EXT_CERT_DESCRIPTION, csr_exts))),
            cert_desp)
        monitor_digests_tup = _prep_data_tup(
            safe_parse_digests(
                pktlab_ext_get_bytes(
                    try_get_extension(
                        pconst.PKTLAB_EXT_MONITOR_DIGESTS, csr_exts))),
            monitor_digests)
        filter_digests_tup  = _prep_data_tup(
            safe_parse_digests(
                pktlab_ext_get_bytes(
                    try_get_extension(
                        pconst.PKTLAB_EXT_FILTER_DIGESTS, csr_exts))),
            filter_digests)
        priority_tup        = _prep_data_tup(
            safe_decode(
                pktlab_ext_get_bytes(
                    try_get_extension(
                        pconst.PKTLAB_EXT_PRIORITY, csr_exts))),
            priority)
        del_type_tup        = _prep_data_tup(
            pktlab_ext_get_bytes(
                try_get_extension(
                    pconst.PKTLAB_EXT_DEL_TYPE, csr_exts)),
            del_type)
    else:
        cert_type_tup       = (cert_type, 2)
        signer_privkey_tup  = (signer_privkey, 2, signer_privkey_name)
        signee_pubkey_tup   = (signee_pubkey, 2, signee_pubkey_name)
        start_time_tup      = (start_time, 2)
        end_time_tup        = (end_time, 2)
        pathlen_tup         = _prep_data_tup(None, pathlen)
        cert_desp_tup       = _prep_data_tup(None, cert_desp)
        monitor_digests_tup = _prep_data_tup(None, monitor_digests)
        filter_digests_tup  = _prep_data_tup(None, filter_digests)
        priority_tup        = _prep_data_tup(None, priority)
        del_type_tup        = _prep_data_tup(None, del_type)

    if not _prompt_input_info(
            cert_type_tup=cert_type_tup,
            signer_privkey_tup=signer_privkey_tup,
            signee_pubkey_tup=signee_pubkey_tup,
            signee_privkey_tup=(None, 0, ""),
            start_time_tup=start_time_tup,
            end_time_tup=end_time_tup,
            pathlen_tup=pathlen_tup,
            cert_desp_tup=cert_desp_tup,
            monitor_digests_tup=monitor_digests_tup,
            filter_digests_tup=filter_digests_tup,
            priority_tup=priority_tup,
            del_type_tup=del_type_tup,
            signrst="certificate",
            ask=ask):
        print("Command aborted")
        return

    if not _is_good_digest_ls(monitor_digests):
        raise ValueError("Bad monitor digest list")
    if not _is_good_digest_ls(filter_digests):
        raise ValueError("Bad filter digest list")

    cert = ppksman.gen_cert(
        name=os.path.basename(path),
        cert_type=cert_type_tup[0],
        signer_privkey=signer_privkey_tup[0],
        signee_pubkey=signee_pubkey_tup[0],
        start_time=start_time_tup[0],
        end_time=end_time_tup[0],
        pathlen=pathlen_tup[0],
        cert_desp=cert_desp_tup[0],
        monitor_digests=_prep_hex_list(monitor_digests_tup[0]),
        filter_digests=_prep_hex_list(filter_digests_tup[0]),
        priority=priority_tup[0],
        del_type=del_type_tup[0])

    if cert is None:
        print("Certificate signing failed; state is not updated")
        return

    with open(path, "w") as fp:
        fp.write(cert.public_bytes(Encoding.PEM).decode())

    print("\nSigned certificate PEM:")
    print(cert.public_bytes(Encoding.PEM).decode(), end="")
    print("Certificate signing succeeded")
    return cert

def _update_argparse_gen_key(subparsers_gen):
    parser_gen_key = subparsers_gen.add_parser(
        "Key", aliases=["key", "k"],
        help="PPKS Manager generate key subcommand")
    parser_gen_key.add_argument(
        "keyname", type=str,
        help="Name for generated Ed25519 key (used in key lists)")
    parser_gen_key.add_argument(
        "-f", "--file", type=str,
        help="Alternative path to store the generated key")
    return

def _update_argparse_gen_csr(subparsers_gen):
    parser_gen_csr = subparsers_gen.add_parser(
        "CertificateSigningRequest", aliases=["CSR", "csr"],
        help="PPKS Manager generate certificate signing request subcommand")
    parser_gen_csr.add_argument(
        "cert_type",
        choices= [
            pconst.PKTLAB_CERTTYPE_STR_SUBCMD,
            pconst.PKTLAB_CERTTYPE_STR_PUBCMD,
            pconst.PKTLAB_CERTTYPE_STR_EXPPRIV,
            pconst.PKTLAB_CERTTYPE_STR_AGENT,
            pconst.PKTLAB_CERTTYPE_STR_DELPRIV],
        help="Certificate signing request type to generate")
    parser_gen_csr.add_argument(
        "signee_privkey", type=str,
        help="Index of or path to private key to generate certificate signing request")
    parser_gen_csr.add_argument(
        "file", type=str,
        help="Path to store generated certificate signing request")
    parser_gen_csr.add_argument(
        "-l", "--pathlen", type=int,
        help="Pathlen in basic constraint extension of certificate signing request")
    parser_gen_csr.add_argument(
        "-c", "--cert_description", type=str,
        help="Certificate description to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "-f", "--filter_digest", nargs='+', type=str,
        help="List of SHA256 hash (in hex) of filter programs to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "-m", "--monitor_digest", nargs='+', type=str,
        help="List of SHA256 hash (in hex) of monitor programs to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "-p", "--priority", type=str,
        help="Priority string to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--del_exppriv", action="store_true",
        help="Specify delegate experiment privilege in certificate signing request")
    parser_gen_csr.add_argument(
        "--del_reppriv", action="store_true",
        help="Specify delegate represent privilege in certificate signing request")
    parser_gen_csr.add_argument(
        "-y", "--yes", action='store_true',
        help="Automatic yes to prompts")
    return

def _update_argparse_gen_cert(subparsers_gen):
    parser_gen_cert = subparsers_gen.add_parser(
        "Certificate", aliases=["certificate", "cert"],
        help="PPKS Manager generate certificate subcommand")
    parser_gen_cert.add_argument(
        "cert_type",
        choices= [
            pconst.PKTLAB_CERTTYPE_STR_SUBCMD,
            pconst.PKTLAB_CERTTYPE_STR_PUBCMD,
            pconst.PKTLAB_CERTTYPE_STR_EXPPRIV,
            pconst.PKTLAB_CERTTYPE_STR_DELPRIV,
            pconst.PKTLAB_CERTTYPE_STR_AGENT],
        help="Certificate type to sign")
    parser_gen_cert.add_argument(
        "signer_privkey", type=str,
        help="Index of or path to signer private key to sign certificate")
    parser_gen_cert.add_argument(
        "start_time", type=int,
        help="Validity period notBefore in signed certificate")
    parser_gen_cert.add_argument(
        "end_time", type=int,
        help="Validity period notAfter in signed certificate")
    parser_gen_cert.add_argument(
        "file", type=str,
        help="Path to store signed certificate")
    parser_gen_cert.add_argument(
        "-k", "--signee_pubkey", type=str,
        help="Index of or path to signee public key to be included in certificate")
    parser_gen_cert.add_argument(
        "-l", "--pathlen", type=int,
        help="Pathlen in basic constraint extension of certificate")
    parser_gen_cert.add_argument(
        "-c", "--cert_description", type=str,
        help="Certificate description to be included in certificate")
    parser_gen_cert.add_argument(
        "-f", "--filter_digest", nargs='+', type=str,
        help="List of SHA256 hash (in hex) of filter programs to be included in certificate")
    parser_gen_cert.add_argument(
        "-m", "--monitor_digest", nargs='+', type=str,
        help="List of SHA256 hash (in hex) of monitor programs to be included in certificate")
    parser_gen_cert.add_argument(
        "-p", "--priority", type=str,
        help="Priority string to be included in certificate")
    parser_gen_cert.add_argument(
        "--del_exppriv", action="store_true",
        help="Specify delegate experiment privilege in certificate")
    parser_gen_cert.add_argument(
        "--del_reppriv", action="store_true",
        help="Specify delegate represent privilege in certificate")
    parser_gen_cert.add_argument(
        "-r", "--csr_path", type=str,
        help="Path to CSR for signing certifcate")
    parser_gen_cert.add_argument(
        "-y", "--yes", action='store_true',
        help="Automatic yes to prompts")
    return

#
# EXPORTED FUNCTIONS
#

def is_gen_subcmd(PPKSMan_subcommand):
    subcmd_set = {"generate", "gen", "g"}
    if PPKSMan_subcommand.lower() in subcmd_set:
        return True
    return False

def update_argparse_gen(subparsers_ppksman):
    parser_gen = subparsers_ppksman.add_parser(
        "Generate", aliases=["generate", "gen", "g"],
        help="PPKS Manager generate subcommand")
    subparsers_gen = parser_gen.add_subparsers(required=True, dest="PPKSMan_gen_subcommand")

    _update_argparse_gen_key(subparsers_gen)
    _update_argparse_gen_csr(subparsers_gen)
    _update_argparse_gen_cert(subparsers_gen)
    return

def subcmd_gen(ppksman, args):
    """
    Main gen command
    """

    if args.PPKSMan_gen_subcommand.lower() in KEY_SUBCMD_SET:
        _genkey(ppksman, args.keyname, args.file)
    elif args.PPKSMan_gen_subcommand.lower() in CSR_SUBCMD_SET:
        print("Loading signee privkey")

        if is_index(args.signee_privkey):
            _, signee_privkey = load_key_ppksman(ppksman, int(args.signee_privkey))
            signee_privkey_name = "from key list index {}".format(args.signee_privkey)
        else:
            _, signee_privkey = load_key_file(args.signee_privkey)
            signee_privkey_name = "from file {}".format(args.signee_privkey)

        if signee_privkey is None:
            raise RuntimeError(
                "Cannot load signee privkey "+
                "(note specified key should only be in privkey list)")

        csr = _sign_csr(
            ppksman=ppksman,
            cert_type=args.cert_type,
            signee_privkey=signee_privkey,
            signee_privkey_name=signee_privkey_name,
            pathlen=args.pathlen,
            cert_desp=args.cert_description,
            monitor_digests=args.monitor_digest,
            filter_digests=args.filter_digest,
            priority=args.priority,
            del_type=comp_del_type(
                args.del_exppriv, args.del_reppriv),
            path=args.file,
            ask=not args.yes)
    elif args.PPKSMan_gen_subcommand.lower() in CERT_SUBCMD_SET:
        csr = None
        if args.csr_path is not None:
            csr = load_csr_file(args.csr_path)
            if not csr.is_signature_valid:
                raise RuntimeError("INVALID certificate signing request signature")

        print("Loading signer privkey")
        if is_index(args.signer_privkey):
            _, signer_privkey = load_key_ppksman(ppksman, int(args.signer_privkey))
            signer_privkey_name = "from key list index {}".format(args.signer_privkey)
        else:
            _, signer_privkey = load_key_file(args.signer_privkey)
            signer_privkey_name = "from file {}".format(args.signer_privkey)

        if signer_privkey is None:
            raise RuntimeError("Cannot load signer privkey")

        # signee pubkey can be supplied either from CSR or list/file
        if args.signee_pubkey is not None:
            print("Loading signee pubkey")

            if is_index(args.signee_pubkey):
                signee_pubkey, _ = load_key_ppksman(ppksman, int(args.signee_pubkey))
                signee_pubkey_name = "from key list index {}".format(args.signee_pubkey)
            else:
                signee_pubkey, _ = load_key_file(args.signee_pubkey)
                signee_pubkey_name = "from file {}".format(args.signee_pubkey)

            if signee_pubkey is None:
                raise RuntimeError("Cannot load signee pubkey")
        else:
            if args.csr_path is None:
                raise ValueError("Either CSR or signee pubkey must be supplied")

            signee_pubkey = None
            signee_pubkey_name = None

        cert = _sign_cert(
            ppksman=ppksman,
            csr=csr,
            cert_type=args.cert_type,
            signer_privkey=signer_privkey,
            signer_privkey_name=signer_privkey_name,
            signee_pubkey=signee_pubkey,
            signee_pubkey_name=signee_pubkey_name,
            start_time=args.start_time,
            end_time=args.end_time,
            pathlen=args.pathlen,
            cert_desp=args.cert_description,
            monitor_digests=args.monitor_digest,
            filter_digests=args.filter_digest,
            priority=args.priority,
            del_type=comp_del_type(
                args.del_exppriv, args.del_reppriv),
            path=args.file,
            ask=not args.yes)
    else:
        raise ValueError(
            "Unknown gen subcommand: {}".format(
                args.PPKSMan_gen_subcommand))
    return