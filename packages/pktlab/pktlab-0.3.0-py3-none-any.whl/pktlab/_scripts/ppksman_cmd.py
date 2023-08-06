#!/usr/bin/python3
#
# Python3 script for the ppksman commandline tool main body.
# *PPKS: PPKS Public Key System, or PacketLab Public Key System
# By TB Yan
# Last updated: 2022/02/02
#

#todo: different verbose level

import argparse
import os

from ..ppks._utils import load_config, KEYMAN_LS, STATEMAN_LS
from ..ppks.PPKSManager import PPKSManager
from .subcmd_init import \
    is_init_subcmd, update_argparse_init, subcmd_init
from .subcmd_gen import \
    is_gen_subcmd, update_argparse_gen, subcmd_gen
from .subcmd_list import \
    is_list_subcmd, update_argparse_list, subcmd_list
from .subcmd_show import \
    is_show_subcmd, update_argparse_show, subcmd_show
from .subcmd_rm import \
    is_remove_subcmd, update_argparse_remove, subcmd_remove
from .subcmd_import import \
    is_import_subcmd, update_argparse_import, subcmd_import

#
# CONSTANTS
#

INTRO_STR = "PyPL PPKS Manager Commandline Interface"

#
# INTERNAL FUNCTIONS
#

def _parse_cmdline():
    parser_main = argparse.ArgumentParser(prog="PPKSMan")
    parser_main.add_argument(
        "-g", "--config",
        help="Path to alternative config file",
        type=str, default=os.path.join(os.path.expanduser("~"), ".pktlab/ppks_conf"))

    subparsers_ppksman = parser_main.add_subparsers(required=True, dest="PPKSMan_subcommand")
    update_argparse_init(subparsers_ppksman)
    update_argparse_gen(subparsers_ppksman)
    update_argparse_list(subparsers_ppksman)
    update_argparse_show(subparsers_ppksman)
    update_argparse_remove(subparsers_ppksman)
    update_argparse_import(subparsers_ppksman)

    return parser_main.parse_args()

def _get_man(configstr_name, class_ls):
    for c in class_ls: # sequential search, sigh
        if configstr_name == c.get_configstr_name():
            return c
    else:
        raise Exception("Cannot found class matching configstr_name. This is a bug.")

def main():
    args = _parse_cmdline()

    # Deal with init as a special case
    if is_init_subcmd(args.PPKSMan_subcommand):
        subcmd_init(args)
        return 0

    #print("Loading config")
    keyman_configstr_tup, stateman_configstr_tup = load_config(args.config)
    if keyman_configstr_tup is None or stateman_configstr_tup is None:
        print("Required configstr(s) not found. Please run init first.")
        return 1

    #print("Loading key manager")
    keyman = _get_man(keyman_configstr_tup[0], KEYMAN_LS)(configstr=keyman_configstr_tup[1])

    #print("Loading state manager")
    stateman = _get_man(stateman_configstr_tup[0], STATEMAN_LS)(configstr=stateman_configstr_tup[1])

    #print("Loading PPKSManager")
    ppksman = PPKSManager(key_manager=keyman, state_manager=stateman)

    #print("")

    if is_gen_subcmd(args.PPKSMan_subcommand):
        subcmd_gen(ppksman, args)
    elif is_list_subcmd(args.PPKSMan_subcommand):
        subcmd_list(ppksman, args)
    elif is_show_subcmd(args.PPKSMan_subcommand):
        subcmd_show(ppksman, args)
    elif is_remove_subcmd(args.PPKSMan_subcommand):
        subcmd_remove(ppksman, args)
    elif is_import_subcmd(args.PPKSMan_subcommand):
        subcmd_import(ppksman, args)
    else:
        raise ValueError(
            "Unknown PPKSMan subcommand: {}".format(
                args.PPKSMan_subcommand))

    keyman.close()
    stateman.close()
    return 0