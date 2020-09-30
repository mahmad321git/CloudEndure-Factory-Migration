"""
TODO add docstring
"""

import os
import sys
import time
import subprocess

from helper import csv_helper
from helper import json_helper
from helper import replication_server_ip_helper

# Path to config.
config_path = 'config\\config.json'
basics_path = 'config\\basics.json'

# Parsing config file.
config = json_helper.parse(config_path)
basics = json_helper.parse(basics_path)

# Python path.
python_path = os.path.join(basics['INSTALL_PYTHON_FOLDER'], 'python.exe')

intake_form = csv_helper.parse(config['INTAKE_FORM'])

# Checks to enable/disable features.
run_import_intake_from_script = True
run_import_tags_script = True
run_ce_agent_install_script = True
run_prerequisites_checks_script = True
run_file_copy_script = True

# Reading wave_ids.
wave_ids = sorted({intake['wave_id']
                   for intake in intake_form})
prerequisite_wave = wave_ids[0]


print("\n===== Workflow Starting: Automation Scripts =====\n")

# =========================== 0-Import-intake-form.py ==========================
if run_import_intake_from_script:
    print("----- Script Starting: 0-Import-intake-form.py -----")

    p = subprocess.Popen(['powershell.exe', python_path, '..\\'
                          'migration_factory\\'
                          'automation_scripts\\0-Import-intake-form.py',
                          '--Intakeform', config['INTAKE_FORM'],
                          '--config', config_path],
                         stdout=sys.stdout)
    p.communicate()

    print("----- Script Completed: 0-Import-intake-form.py -----\n")
    print("----- ========================================= -----")


# ============================== 0-Import-tags.py ==============================
if run_import_tags_script:
    print("----- Script Starting: 0-Import-tags.py -----")

    p = subprocess.Popen(['powershell.exe', python_path, '..\\'
                          'migration_factory\\'
                          'automation_scripts\\0-Import-tags.py',
                          '--Intakeform', config['INTAKE_TAGS'],
                          '--config', config_path], stdout=sys.stdout)
    p.communicate()

    print("----- Script Completed: 0-Import-tags.py -----\n")
    print("----- ========================================= -----")


# ============================= 1-CEAgentInstall.py ============================
if run_ce_agent_install_script:
    print("----- Script Workflow: 1-CEAgentInstall.py -----")
    for wave_id in wave_ids:
        print(f"----- Starting for Wave ID {wave_id}... -----")
        p = subprocess.Popen(['powershell.exe', python_path, '..\\'
                              'migration_factory\\automation_scripts\\'
                              '1-CEAgentInstall.py',
                              '--Waveid', wave_id,
                              '--config', config_path],
                             stdout=sys.stdout)
        p.communicate()

        if run_prerequisites_checks_script and wave_id == prerequisite_wave:
            print('Waiting for Replication Server to start...')
            time.sleep(300)
            replication_server_ip = replication_server_ip_helper \
                .get_replication_server_ip()

            if not replication_server_ip:
                print('Replication server not up... ignoring prerequisite'
                      ' checks.')
                continue

            for wave_id in wave_ids:
                print(f"----- Prerequisites check for Wave ID {wave_id}... "
                      "-----")
                p = subprocess.Popen(['powershell.exe', python_path, '..\\'
                                      'migration_factory\\automation_scripts\\'
                                      '0-Prerequistes-checks.py',
                                      '--Waveid', wave_id,
                                      '--CEServerIP', replication_server_ip,
                                      '--config', config_path],
                                     stdout=sys.stdout)
                p.communicate()

    print("----- Script Completed: 1-CEAgentInstall.py -----\n")
    print("----- ========================================= -----")


# ============================= 1-FileCopy-Linux.py ============================
if run_file_copy_script:
    if os.path.exists(config['FILE_COPY']):
        print("----- Script Workflow: 1-FileCopy-Linux.py -----")
        for wave_id in wave_ids:
            print(f"----- Starting for Wave ID {wave_id}... -----")
            p = subprocess.Popen(['powershell.exe', python_path, '..\\'
                                  'migration_factory\\automation_scripts\\'
                                  '1-FileCopy-Linux.py',
                                  '--Waveid', wave_id,
                                  '--Source', config['file_copy'],
                                  '--config', config_path],
                                 stdout=sys.stdout)
            p.communicate()
        print("----- Script Completed: 1-FileCopy-Linux.py -----\n")
        print("----- ========================================= -----")

# ============================ 1-FileCopy-Windows.py ===========================
        print("----- Script Workflow: 1-FileCopy-Windows.py -----")
        for wave_id in wave_ids:
            print(f"----- Starting for Wave ID {wave_id}... -----")
            p = subprocess.Popen(['powershell.exe', python_path, '..\\'
                                  'migration_factory\\automation_scripts\\'
                                  '1-FileCopy-Windows.py',
                                  '--Waveid', wave_id,
                                  '--Source', config['file_copy'],
                                  '--config', config_path],
                                 stdout=sys.stdout)
            p.communicate()
        print("----- Script Completed: 1-FileCopy-Windows.py -----\n")
        print("----- ========================================= -----")


# ============================= 2-UserMgmt-Linux.py ============================
# print("----- Script Workflow: 2-UserMgmt-Linux.py -----")
# for wave_id in wave_ids:
#     print(f"----- Starting for Wave ID {wave_id}... -----")
#     p = subprocess.Popen(['powershell.exe', python_path, '..\\'
#                           'migration_factory\\automation_scripts\\'
#                           '2-UserMgmt-Linux.py',
#                           '--Waveid', wave_id,
#                           '--config', config_path],
#                          stdout=sys.stdout)
#     p.communicate()
# print("----- Script Completed: 2-UserMgmt-Linux.py -----\n")
# print("----- ========================================= -----")


# ============================ 2-UserMgmt-Windows.py ===========================
# print("----- Script Workflow: 2-UserMgmt-Windows.py -----")
# for wave_id in wave_ids:
#     print(f"----- Starting for Wave ID {wave_id}... -----")
#     p = subprocess.Popen(['powershell.exe', python_path, '..\\'
#                           'migration_factory\\automation_scripts\\'
#                           '2-UserMgmt-Windows.py',
#                           '--Waveid', wave_id,
#                           '--config', config_path],
#                          stdout=sys.stdout)
#     p.communicate()
# print("----- Script Completed: 2-UserMgmt-Windows.py -----\n")
# print("----- ========================================= -----")


# =========================== 2-Verify-replication.py ==========================
# print("----- Script Workflow: 2-Verify-replication.py -----")
# for wave_id in wave_ids:
#     print(f"----- Starting for Wave ID {wave_id}... -----")
#     p = subprocess.Popen(['powershell.exe', python_path, '..\\'
#                           'migration_factory\\automation_scripts\\'
#                           '2-Verify-replication.py',
#                           '--Waveid', wave_id,
#                           '--config', config_path],
#                          stdout=sys.stdout)
#     p.communicate()
# print("----- Script Completed: 2-Verify-replication.py -----\n")
# print("----- ========================================= -----")
