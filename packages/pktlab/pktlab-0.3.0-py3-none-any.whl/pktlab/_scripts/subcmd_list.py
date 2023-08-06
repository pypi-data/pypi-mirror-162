#!/usr/bin/python3
#
# Python3 script for the ppksman commandline tool list subcmd.
# The list subcmd allows listing PPKS CSRs, certificates and keys stored by submanagers.
# *PPKS: PPKS Public Key System, or PacketLab Public Key System
# By TB Yan
# Last updated: 2022/02/02
#

from ..ppks._utils import \
    KEY_SUBCMD_SET, CSR_SUBCMD_SET, CERT_SUBCMD_SET

def _list_names(start_output, name_ls, start_indx=0):
    print(start_output)
    for i, name in enumerate(name_ls):
        print("\t{}. {}".format(i+start_indx, name))
    return

def _list_csr(ppksman):
    _list_names(
        start_output="Certificate signing request list:",
        name_ls=ppksman.get_past_csr_list())
    return

def _list_cert(ppksman):
    _list_names(
        start_output="Certificate list:",
        name_ls=ppksman.get_past_cert_list())
    return

def _list_key(ppksman):
    pubkey_ls = ppksman.get_pubkey_list()
    privkey_ls = ppksman.get_privkey_list()

    _list_names("pubkey list:", pubkey_ls)
    _list_names("privkey list:", privkey_ls, start_indx=len(pubkey_ls))
    return

def _update_argparse_list_key(subparsers_list):
    subparsers_list.add_parser(
        "Key", aliases=["key", "k"],
        help="PPKS Manager list key subcommand")
    return

def _update_argparse_list_csr(subparsers_list):
    subparsers_list.add_parser(
        "CertificateSigningRequest", aliases=["CSR", "csr"],
        help="PPKS Manager list certificate signing request subcommand")
    return

def _update_argparse_list_cert(subparsers_list):
    subparsers_list.add_parser(
        "Certificate", aliases=["certificate", "cert"],
        help="PPKS Manager list certificate subcommand")
    return

#
# EXPORTED FUNCTIONS
#

def is_list_subcmd(PPKSMan_subcommand):
    subcmd_set = {"list", "ls", "l"}
    if PPKSMan_subcommand.lower() in subcmd_set:
        return True
    return False

def update_argparse_list(subparsers_ppksman):
    parser_list = subparsers_ppksman.add_parser(
        "List", aliases=["list", "ls", "l"],
        help="PPKS Manager list subcommand")
    subparsers_list = parser_list.add_subparsers(
        required=True, dest="PPKSMan_list_subcommand")

    _update_argparse_list_key(subparsers_list)
    _update_argparse_list_csr(subparsers_list)
    _update_argparse_list_cert(subparsers_list)
    return

def subcmd_list(ppksman, args):
    if args.PPKSMan_list_subcommand.lower() in KEY_SUBCMD_SET:
        _list_key(ppksman)
    elif args.PPKSMan_list_subcommand.lower() in CSR_SUBCMD_SET:
        _list_csr(ppksman)
    elif args.PPKSMan_list_subcommand.lower() in CERT_SUBCMD_SET:
        _list_cert(ppksman)
    else:
        raise ValueError(
            "Unknown list subcommand: {}".format(
                args.PPKSMan_list_subcommand))