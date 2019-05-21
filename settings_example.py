SAVE_PATH = '/var/lib/backups/mymachines'
TEMP_PATH = '/tmp'

CLIENTS = [
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
