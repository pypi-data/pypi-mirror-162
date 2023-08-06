#
# Python3 script for the ppksman commandline tool rm subcmd.
# The rm subcmd allows removing PPKS keys, CSRs and certificates stored by submanagers.
# *PPKS: PPKS Public Key System, or PacketLab Public Key System
# By TB Yan
# Last updated: 2022/02/02
#

from ..ppks._utils import \
    yes_no_prompt, \
    KEY_SUBCMD_SET, CSR_SUBCMD_SET, CERT_SUBCMD_SET

#
# INTERNAL FUNCTIONS
#

def _remove_key(ppksman, key_target, yes):
    if key_target < 0:
        raise IndexError("Bad list index")

    if not yes and \
       not yes_no_prompt(
                start_text="Remove key of index {} in list? (y/N) ".format(key_target),
                fail_text="Unrecognized input, please try again",
                default=-1):
        print("Command aborted")
        return

    pubkey_ls = ppksman.get_pubkey_list()
    if len(pubkey_ls) <= key_target:
        ppksman.remove_privkey(key_target-len(pubkey_ls))
    else:
        ppksman.remove_pubkey(key_target)
    print("Key of index {} removed".format(key_target))
    return

def _remove_csr(ppksman, csr_target, yes):
    if csr_target < 0:
        raise IndexError("Bad list index")

    if not yes and \
       not yes_no_prompt(
                start_text="Remove certificate signing request of index {} in list? (y/N) ".format(csr_target),
                fail_text="Unrecognized input, please try again",
                default=-1):
        print("Command aborted")
        return

    ppksman.remove_past_csr(csr_target)
    print("Certificate signing request of index {} removed".format(csr_target))
    return

def _remove_cert(ppksman, cert_target, yes):
    if cert_target < 0:
        raise IndexError("Bad list index")

    if not yes and \
       not yes_no_prompt(
                start_text="Remove certificate of index {} in list? (y/N) ".format(cert_target),
                fail_text="Unrecognized input, please try again",
                default=-1):
        print("Command aborted")
        return

    ppksman.remove_past_cert(cert_target)
    print("Certificate of index {} removed".format(cert_target))
    return

def _update_argparse_remove_key(subparsers_remove):
    parser_remove_key = subparsers_remove.add_parser(
        "Key", aliases=["key", "k"],
        help="PPKS Manager remove key subcommand")
    parser_remove_key.add_argument(
        "key_target", type=int,
        help='Index of specific key in list for removal')
    parser_remove_key.add_argument(
        "-y", "--yes", action='store_true',
        help="Automatic yes to prompts")
    return

def _update_argparse_remove_csr(subparsers_remove):
    parser_remove_csr = subparsers_remove.add_parser(
        "CertificateSigningRequest", aliases=["CSR", "csr"],
        help="PPKS Manager remove certificate signing request subcommand")
    parser_remove_csr.add_argument(
        "csr_target", type=int,
        help='Index of specific certificate signing request in list for removal')
    parser_remove_csr.add_argument(
        "-y", "--yes", action='store_true',
        help="Automatic yes to prompts")
    return

def _update_argparse_remove_cert(subparsers_remove):
    parser_remove_cert = subparsers_remove.add_parser(
        "Certificate", aliases=["certificate", "cert"],
        help="PPKS Manager remove certificate subcommand")
    parser_remove_cert.add_argument(
        "cert_target", type=int,
        help='Index of specific certificate in list for removal')
    parser_remove_cert.add_argument(
        "-y", "--yes", action='store_true',
        help="Automatic yes to prompts")
    return

#
# EXPORTED FUNCTIONS
#

def is_remove_subcmd(PPKSMan_subcommand):
    subcmd_set = {"remove", "rm", "r"}
    if PPKSMan_subcommand.lower() in subcmd_set:
        return True
    return False

def update_argparse_remove(subparsers_ppksman):
    parser_remove = subparsers_ppksman.add_parser(
        "Remove", aliases=["remove", "rm", "r"],
        help="PPKS Manager remove subcommand")
    subparsers_remove = parser_remove.add_subparsers(
        required=True, dest="PPKSMan_remove_subcommand")

    _update_argparse_remove_key(subparsers_remove)
    _update_argparse_remove_csr(subparsers_remove)
    _update_argparse_remove_cert(subparsers_remove)
    return

def subcmd_remove(ppksman, args):
    if args.PPKSMan_remove_subcommand.lower() in KEY_SUBCMD_SET:
        _remove_key(ppksman, args.key_target, args.yes)
    elif args.PPKSMan_remove_subcommand.lower() in CSR_SUBCMD_SET:
        _remove_csr(ppksman, args.csr_target, args.yes)
    elif args.PPKSMan_remove_subcommand.lower() in CERT_SUBCMD_SET:
        _remove_cert(ppksman, args.cert_target, args.yes)
    else:
        raise ValueError(
            "Unknown remove subcommand: {}".format(
                args.PPKSMan_remove_subcommand))