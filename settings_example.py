SAVE_PATH = '/var/lib/backups/mymachines'
TEMP_PATH = '/tmp'

HOSTS = [
    {
        'name': 'web1',
        'host': 'example.com',
        'user': 'server_backup',
        'plugins': {
            'file': {
                'paths': ('/etc/',),
            }
        },
    }
]
