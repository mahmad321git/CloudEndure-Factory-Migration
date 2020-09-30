# Migration Execution Server

<!-- TODO: Write a readme documentation. -->
Work in progress.

## Observation and decisions to be made

- Handling Project Name in Migration Factory:
  - Option 1: Separate script
  - Option 2: part of 0-Import-intake-form.py (added projects not present in the MF but will require admin api)
- VPC
  - Subnet
  - Security Group (3389 and 22)
- Project Name in Migration Factory should be present before starting automation scripts.
- `0-Prerequistes-checks.py` script requires at least one source server to have CEAgent installed.
- `1-CEAgentInstall.py` tested on wave id 1.
  - `1-CEAgentInstall.py` at the end says installation failed but its a false alarm. (to be investigated)
  - `1-CEAgentInstall.py` Fails for windows due to credential issues
