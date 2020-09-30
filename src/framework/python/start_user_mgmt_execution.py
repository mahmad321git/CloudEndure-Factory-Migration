"""
TODO add docstring
"""

import os
import sys
import argparse
import subprocess

from helper import csv_helper
from helper import json_helper

# Parsing arugments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--modification', required=True)
parser.add_argument('--username', required=True)
parser.add_argument('--password', required=True)
args = parser.parse_args(sys.argv[1:])

# Path to config.
config_path = 'config\\config.json'
basics_path = 'config\\basics.json'

# Parsing config file.
config = json_helper.parse(config_path)
basics = json_helper.parse(basics_path)

# Python path.
python_path = os.path.join(basics['INSTALL_PYTHON_FOLDER'], 'python.exe')

intake_form = csv_helper.parse(config['INTAKE_FORM'])

# Reading wave_ids.
wave_ids = sorted({intake['wave_id']
                   for intake in intake_form})


print("\n===== Workflow Starting: User Management =====\n")

# ============================= 2-UserMgmt-Linux.py ===========================
print("----- Script Workflow: 2-UserMgmt-Linux.py -----")
for wave_id in wave_ids:
    print(f"----- Starting for Wave ID {wave_id}... -----")
    p = subprocess.Popen(['powershell.exe', python_path, '..\\'
                          'migration_factory\\automation_scripts\\'
                          '2-UserMgmt-Linux.py',
                          '--Waveid', wave_id,
                          '--config', config_path,
                          '--username', args.username,
                          '--password', args.password,
                          '--modification', args.modification],
                         stdout=sys.stdout)
    p.communicate()
print("----- Script Completed: 2-UserMgmt-Linux.py -----\n")
print("----- ========================================= -----")


# ============================ 2-UserMgmt-Windows.py ==========================
print("----- Script Workflow: 2-UserMgmt-Windows.py -----")
for wave_id in wave_ids:
    print(f"----- Starting for Wave ID {wave_id}... -----")
    p = subprocess.Popen(['powershell.exe', python_path, '..\\'
                          'migration_factory\\automation_scripts\\'
                          '2-UserMgmt-Windows.py',
                          '--Waveid', wave_id,
                          '--config', config_path,
                          '--username', args.username,
                          '--password', args.password,
                          '--modification', args.modification],
                         stdout=sys.stdout)
    p.communicate()
print("----- Script Completed: 2-UserMgmt-Windows.py -----\n")
print("----- ========================================= -----")
