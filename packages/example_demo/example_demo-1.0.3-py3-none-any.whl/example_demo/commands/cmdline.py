# -*- coding: utf-8 -*-


import sys
from os.path import dirname, join

from example_demo.commands import create_builder
from example_demo.commands import start_program
# import start_program
# from example_demo.commands import zip


def _print_commands():
    print('start')
    print(dirname(dirname(__file__)))
    with open(join(dirname(dirname(__file__)), "__version__.py"), "rb") as f:
        version = f.read().decode("ascii").strip()

    print("onedatautil {}".format(version))
    print("\nUsage:")
    print("  onedatautil <command> [options] [args]\n")
    print("Available commands:")
    cmds = {
        "create": "create project",
        "start": "start project",
        # "zip": "zip project",
    }
    for cmdname, cmdclass in sorted(cmds.items()):
        print("  %-13s %s" % (cmdname, cmdclass))

    print('\nUse "onedatautil <command> -h" to see more info about a command')


def execute():
    args = sys.argv
    if len(args) < 2:
        _print_commands()
        return

    command = args.pop(1)
    if command == "generate":
        create_builder.main()
    # elif command == "start":
    #     start_program.main()
    # elif command == "zip":
    #     zip.main()
    else:
        _print_commands()
if __name__ == "__main__":
    execute()