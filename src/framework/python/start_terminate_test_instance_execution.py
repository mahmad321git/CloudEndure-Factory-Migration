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

# Reading wave_ids.
wave_ids = sorted({intake['wave_id']
                   for intake in csv_helper
                   .parse(config['INTAKE_FORM'])})


print("\n===== Workflow Starting: Automation Scripts =====\n")

# ============================= 3-Terminate-test-instance.py ============================
print("----- Script Workflow: 3-Terminate-test-instance.py -----")
for wave_id in wave_ids:
    print(f"----- Starting for Wave ID {wave_id}... -----")
    p = subprocess.Popen(['powershell.exe', python_path, '..\\'
                          'migration_factory\\automation_scripts\\'
                          '3-Terminate-test-instance.py',
                          '--Waveid', wave_id,
                          '--config', config_path],
                         stdout=sys.stdout)
    p.communicate()
print("----- Script Completed: 3-Terminate-test-instance.py -----\n")
print("----- ========================================= -----")
