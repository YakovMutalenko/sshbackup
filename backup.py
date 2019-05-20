import core
import logger
import logging
import plugins
import settings


@core.single_process
def main():
    logger.configure()
    
    logging.info('Found %s clients for backup', len(settings.CLIENTS))

    for conf in settings.CLIENTS:
        client = core.Client.from_dict(conf)

        plugins = conf.get('plugins', {})
        for shortcut in plugins:
            plugin = core.import_class(settings.PLUGINS[shortcut])
            instance = plugin(client, plugins[shortcut])
            client.add_plugin(instance)

        client.backup()

    logging.info('The backup process completed')


if __name__ == "__main__":
    main()
