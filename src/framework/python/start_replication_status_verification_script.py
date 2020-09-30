"""
TODO add docstring
"""

import os
import sys
import subprocess

from helper import csv_helper
from helper import json_helper

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
prerequisite_wave = wave_ids[0]


print("\n===== Workflow Starting: Automation Scripts =====\n")


# =========================== 2-Verify-replication.py =========================
print("----- Script Workflow: 2-Verify-replication.py -----")
for wave_id in wave_ids:
    print(f"----- Starting for Wave ID {wave_id}... -----")
    p = subprocess.Popen(['powershell.exe', python_path, '..\\'
                          'migration_factory\\automation_scripts\\'
                          '2-Verify-replication.py',
                          '--Waveid', wave_id,
                          '--config', config_path],
                         stdout=sys.stdout)
    p.communicate()
print("----- Script Completed: 2-Verify-replication.py -----\n")
print("----- ========================================= -----")
