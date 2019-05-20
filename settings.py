SAVE_PATH = './'
TEMP_PATH = './tmp'

# If you would like to bypass the verification step,
# you can set the "StrictHostKeyChecking" option to "no" on the command line:
# SSH_OPTS = '-o "StrictHostKeyChecking=no"'
SSH_OPTS = ''

# Set or unset values of shell options and positional parameters.
# Options:
# -e Exit immediately if a command exits with a non-zero status.
# -o option-name
#       Set the variable corresponding to option-name:
#           errexit      same as -e
#           pipefail     the return value of a pipeline is the status of
#                        the last command to exit with a non-zero status,
#                        or zero if no command exited with a non-zero status
SHELL_OPTS = 'set -o pipefail -o errexit'

# The maximum number of backups.
# Redundant files will be removed after a successful creation of a new backup.
# Comfortable values are:
# * 22 (equals 22 business day backups)
# * 30 (equals day backups)
MAX_BACKUP_COUNT = 3

PLUGINS = {
    'file': 'plugins.FileBackup',
    'mysql': 'plugins.MySQLBackup',
    'postgresql': 'plugins.PostgreSQLBackup'
}

try:
    from settings_local import *
except ImportError:
    pass