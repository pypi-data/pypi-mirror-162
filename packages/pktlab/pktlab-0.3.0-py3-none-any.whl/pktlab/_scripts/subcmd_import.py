#
# Python3 script for the ppksman commandline tool import subcmd.
# The import subcmd allows importing PPKS keys.
# *PPKS: PPKS Public Key System, or PacketLab Public Key System
# By TB Yan
# Last updated: 2022/02/02
#

import os

#
# INTERNAL FUNCTIONS
#

def _import_key(ppksman, path):
    with open(path, "r") as fp:
        keystr = fp.read()

    name = os.path.basename(os.path.abspath(path))
    if name[-4:] == ".pub":
        ppksman.import_pubkey(keystr, name)
    else:
        ppksman.import_privkey(keystr, name)
    print("Import key (from {}) completed".format(path))
    return

#
# EXPORTED FUNCTIONS
#

def is_import_subcmd(PPKSMan_subcommand):
    subcmd_set = {"import", "imp"}
    if PPKSMan_subcommand.lower() in subcmd_set:
        return True
    return False

def update_argparse_import(subparsers_ppksman):
    parser_import = subparsers_ppksman.add_parser(
        "Import", aliases=["import", "imp"],
        help="PPKS Manager import key subcommand")
    parser_import.add_argument(
        "path", type=str,
        help='Path to key PEM file for importing')
    return

def subcmd_import(ppksman, args):
    _import_key(ppksman, args.path)
    return