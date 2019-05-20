import datetime as dt
import logging
import os
import shutil
import subprocess
import tempfile

import settings
import validators


class Plugin:
    validators = []

    def __init__(self, client, params=None):
        self.client = client
        self.params = params or {}

    def __str__(self):
        return '{backup}@{client}'.format(
            backup=self.name,
            client=self.client
        )

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def save_path(self):
        return os.path.join(settings.SAVE_PATH, self.client.name, self.name)

    @property
    def file_path(self):
        return os.path.join(self.save_path, self.file_name)

    @property
    def file_prefix(self):
        return dt.datetime.now().strftime("%Y-%m-%d_%H-%M")

    @property
    def file_name(self):
        raise NotImplementedError

    @property
    def command(self):
        raise NotImplementedError

    @property
    def popen_args(self):
        """
        Return list of args that will be passed to Popen initializer.
        """
        cmd = (
            'ssh {ssh_opts} {host} -p {port} -l {user} '
            '{shell_opts}; {command}'
        ).format(
            ssh_opts=settings.SSH_OPTS,
            host=self.client.host,
            port=self.client.port,
            user=self.client.user,
            shell_opts=settings.SHELL_OPTS,
            command=self.command
        )
        return cmd.split()

    def validate(self):
        return all([v(self.file_path) for v in self.validators])

    def copy_to_destination(self, tmp_path):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
            logging.debug('Created a new directory: %s', self.save_path)
        shutil.copy(tmp_path, self.file_path)
        logging.debug('Backup copied successfully to %s', self.file_path)

    def create(self):
        fd, tmp_path = tempfile.mkstemp(dir=settings.TEMP_PATH)
        try:
            with os.fdopen(fd, 'w') as tmp:
                p = subprocess.Popen(
                    self.popen_args, stdout=tmp, stderr=subprocess.PIPE)
                logging.debug('Waiting for streaming process to terminate')
                _, errors = p.communicate()
                if p.returncode:
                    error_msg = '{instance}\n{errors}'.format(
                        instance=self,
                        errors=errors.decode().strip()
                    )
                    logging.error(error_msg)
                else:
                    self.copy_to_destination(tmp_path)
                    if self.validate():
                        self.rotate()
        finally:
            os.remove(tmp_path)

    def rotate(self):
        logging.debug('Running rotation mechanism')

        backups = []
        for root, _, files in os.walk(self.save_path):
            backups = sorted([os.path.join(root, f)
                              for f in files], reverse=True)

        outdated = backups[settings.MAX_BACKUP_COUNT:]

        logging.debug('Found %s backups of "%s" created by %s. Old backups: %s',
                      len(backups), self.client.name, self.name, len(outdated))

        for f in outdated:
            os.remove(f)
            logging.debug('File %s removed, because outdated.', f)


class FileBackup(Plugin):
    """ Create file backup with GNU tar. """

    validators = [validators.gzip_validator]

    @property
    def file_name(self):
        return self.file_prefix + '.tar.gz'

    @property
    def command(self):
        """
        Return string of args that will be used with popen_args property.
        """
        return 'sudo tar -cf - %s --warning=no-file-changed | gzip -c' % self._get_paths()

    def _get_paths(self):
        """
        Return paths to change working directory and directory name of target path
        like this: '-C /working_dir target_dir'.
        """
        tar_paths = []
        for path in self.params['paths']:
            normpath = os.path.normpath(path)
            if normpath == os.sep:
                target_dir = normpath
            else:
                change_dir, target_dir = os.path.split(normpath.rstrip(os.sep))
                tar_paths.extend(['-C', change_dir])
            tar_paths.extend([target_dir])
        return ' '.join(tar_paths)


class MySQLBackup(Plugin):
    """
    Create MySQL dump with mysqldump utility;
    mysqldump reads database credentials from .my.cnf file.
    """
    validators = [validators.gzip_validator]

    @property
    def file_name(self):
        return self.file_prefix + '.gz'

    @property
    def command(self):
        """
        Return string of args that will be used with popen_args property
        """
        cmd = "mysqldump -u {db_user} {params} {db_name} | gzip -c".format(
            db_user=self.params['user'],
            db_name=self.params['database'],
            params=self.params.get('params', '')
        )
        return cmd


class PostgreSQLBackup(Plugin):
    """
    Create PostgreSQL dump with pg_dumpall utility.
    """
    validators = [validators.gzip_validator]

    @property
    def file_name(self):
        return self.file_prefix + '.gz'

    @property
    def command(self):
        """
        Return string of args that will be used with popen_args property.
        """
        cmd = "pg_dumpall {params} | gzip -c".format(
            params=self.params.get('params', '')
        )
        return cmd
