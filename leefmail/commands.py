#!/usr/bin/env python

# ############################################################################
# This is the code for THE leefmail command line program
# and all it's related commands
# ############################################################################

import os
import sys
import begin

import leefmail

# TODO: remove below if statement asap. This is a workaround for a bug in begins
# TODO: which provokes an eception when calling pypeman without parameters.
# TODO: more info at https://github.com/aliles/begins/issues/48
if len(sys.argv) == 1:
    sys.argv.append('-h')

# Keep this import
sys.path.insert(0, os.getcwd())

@begin.subcommand
def start(reload: 'Make server autoreload (Dev only)'=False,):
    """ Start leefmail """
    print('toto')

@begin.start
def run(version=False):
    """ Leefmail """
    if version:
        print(leefmail.__version__)
        sys.exit(0)