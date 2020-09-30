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

# Change this to true to enable this script.
run_shutdown_all_servers_script = False

# Reading wave_ids.
wave_ids = sorted({intake['wave_id']
                   for intake in csv_helper
                   .parse(config['INTAKE_FORM'])})


print("\n===== Workflow Starting: Automation Scripts =====\n")

# ========================== 4-Shutdown-all-servers.py ========================
if run_shutdown_all_servers_script:
    print("----- Script Workflow: 4-Shutdown-all-servers.py -----")
    for wave_id in wave_ids:
        print(f"----- Starting for Wave ID {wave_id}... -----")
        p = subprocess.Popen(['powershell.exe', python_path, '..\\'
                              'migration_factory\\automation_scripts\\'
                              '4-Shutdown-all-servers.py',
                              '--Waveid', wave_id,
                              '--config', config_path],
                             stdout=sys.stdout)
        p.communicate()
    print("----- Script Completed: 4-Shutdown-all-servers.py -----\n")
    print("----- ========================================= -----")
else:
    print('WARNING: This script has been disabled as it will shutdown'
          ' all source servers. To activate it, open script '
          'cloud-migration-automation-framework\\src\\framework'
          '\\python\\start_shutdown_all_servers.py and update line 24 with'
          '"run_shutdown_all_servers_script = True".')
