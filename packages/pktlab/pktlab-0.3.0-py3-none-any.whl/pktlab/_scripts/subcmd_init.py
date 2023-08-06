#
# Python3 script for the ppksman commandline tool init subcmd.
# The init subcmd is for initializing PPKSMan (mostly the submanagers).
# *PPKS: PPKS Public Key System, or PacketLab Public Key System
# By TB Yan
# Last updated: 2022/02/02
#

import os

from ..ppks._utils import \
    is_index, load_config, \
    list_names, yes_no_prompt, \
    KEYMAN_LS, STATEMAN_LS

#
# INTERNAL FUNCTIONS
#

def _init_select_prompt(select_output, class_ls):
    while True:
        list_names(select_output, [c.get_print_name() for c in class_ls])

        indx = input("Please enter you choice in index (0 ~ {}): ".format(len(class_ls)-1))
        if not is_index(indx) or int(indx) >= len(class_ls):
            print("Cannot understand input. Please try again.")
            continue
        break

    man = class_ls[int(indx.strip())].prompt()
    man_tup = (man.get_configstr_name(), man.get_configstr())
    return man_tup

def _init(config_path):
    keyman_tup, stateman_tup = load_config(config_path)
    prompt_overwrite = should_dump = False

    if keyman_tup is not None or stateman_tup is not None:
        prompt_overwrite = True

    print("Initializing PPKSManager")

    if keyman_tup is None:
        print("KeyManager configstr not found. Initializing ...")
        should_dump = True
        keyman_tup = _init_select_prompt("Select key manager to use:", KEYMAN_LS)
    else:
        print("Detected KeyManager configstr: {}".format(keyman_tup[0]))

    if stateman_tup is None:
        print("StateManager configstr not found. Initializing ...")
        should_dump = True
        stateman_tup = _init_select_prompt("Select state manager to use:", STATEMAN_LS)
    else:
        print("Detected StateManager configstr: {}".format(stateman_tup[0]))

    if should_dump:
        if prompt_overwrite:
            if not yes_no_prompt(
                    start_text="Config file updated, proceed to overwrite? (y/N) ",
                    fail_text="Unrecognized input, please try again"):
                print("Config file not updated; initialization aborted")
                return

        print("Config file updated")
        _dump_config(config_path, keyman_tup, stateman_tup)

    print("Initialization completed")
    return

def _dump_config(path, keyman_configstr_tup, stateman_configstr_tup):
    config_dirpath = os.path.dirname(os.path.abspath(path))
    if not os.path.exists(config_dirpath):
        os.makedirs(config_dirpath, mode=0o700, exist_ok=True)

    with open(path, "w") as fp:
        if keyman_configstr_tup is not None:
            fp.write("{} {}\n".format(keyman_configstr_tup[0], keyman_configstr_tup[1]))

        if stateman_configstr_tup is not None:
            fp.write("{} {}\n".format(stateman_configstr_tup[0], stateman_configstr_tup[1]))
    return

#
# EXPORTED FUNCTIONS
#

def is_init_subcmd(PPKSMan_subcommand):
    subcmd_set = {"initialize", "init"}
    if PPKSMan_subcommand.lower() in subcmd_set:
        return True
    return False

def update_argparse_init(subparsers_ppksman):
    subparsers_ppksman.add_parser(
        "Initialize", aliases=["initialize", "init"],
        help="PPKS Manager initialize subcommand")
    # init is done interactively for now
    return

def subcmd_init(args):
    _init(args.config)
    return