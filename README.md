# SSH Backup

This script creates remote backups. It let's remote machines stream it's data to your machine using the SSH connection.

There are plugins available that provide functionality.

Python 3 required.

Tested with Debian 8/9, MacOS 10 & Centos 7.6.

## Features and Plugins

* User files backup (provided by `FileBackup` plugin);
* MySQL database backup (provided by `MySQLBackup` plugin).
* PostgreSQL database backup (provided by `PostgreSQLBackup` plugin).

The script comes with backup rotating feature.

## Installation

### Server Setup
1. Clone a project repo.
2. Generate SSH keys for clients:
	```
	$ ssh-keygen ~/.ssh/server_backup
	```
3. Add host key to `~/.ssh/known_hosts`, for example:
	```
	$ ssh-keyscan example.com >> ~/.ssh/known_hosts
	```
4. Create `settings_local.py` file and override settings from `settings.py` (see `settings_example.py`).

5. Configure cron task like this:
	```
	20 22 * * 1,2,3,4,5 python3 /opt/debian-ssh-backup/backup.py
	```

	This equals business day backups. If you need to change this, 
	make sure the `MAX_BACKUP_COUNT` variable from `settings_local` is set correctly.
	```

### Client Setup
1. Create system user for the script:
	```
	# useradd server_backup -m
	```
2. Create SSH config directory:
	```
	# su server_backup
	$ cd /home/server_backup && mkdir .ssh && chmod 700 .ssh && cd .ssh
	```
3. Add `server_backup.pub` key to the authorized_keys file.
4. Allow to run archive command as root without password. Please run:
	```
	# visudo
	```
	and add this line:
	```
	server_backup ALL = (root) NOPASSWD: /bin/tar
	```

5. Configure MySQL or PostgreSQL backup.

#### Configure MySQL Backup

1. Create MySQL user and grant permissions for backup, for example:
	```mysql
	CREATE USER 'server_backup' IDENTIFIED BY '<your password here>';
	GRANT SELECT, FILE, SHOW DATABASES, CREATE TEMPORARY TABLES, LOCK TABLES, SHOW VIEW, EVENT ON \*.\* TO 'server_backup'@'localhost';
	FLUSH PRIVILEGES;
	```
2. Create file `/home/server_backup/.my.cnf` with content like this:
	```
	[mysqldump]
	user=server_backup
	password=<your password here>
	```
#### Configure PostgreSQL Backup

1. Login `psql` as `postgres` or other superuser.
2. Create the new superuser role and set it to read only:
	```mysql
	CREATE USER server_backup SUPERUSER password '<PASS>';
	ALTER USER server_backup set default_transaction_read_only = on;
	```
Do not forgot the single quotes for the password. You can now use this role to backup.

## Usage

`python3 backup.py`

## Author
Eugene Zyatev ([eu@zyatev.ru](mailto:eu@zyatev.ru))