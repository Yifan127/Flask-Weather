import logging

LOGGING = {'version': 1,
           'handlers': {'fileHandler': {
                            'class': 'logging.handlers.RotatingFileHandler',
                            'formatter': 'myFormatter',
                            'filename': 'weather.log',
                            'maxBytes': 10000,
                            'backupCount': 5},
                        'console': {
                            'class': 'logging.StreamHandler',
                            'formatter': 'myFormatter',
                            'level': logging.INFO}
                        },
           'loggers': {'filelogger': {
                           'handlers': ['fileHandler', 'console'],
                           'level': logging.INFO}
                       },
           'formatters': {
                'myFormatter': {
                      'format': '%(asctime)s %(levelname)s: %(message)s '
                                '[in %(module)s - %(funcName)s:%(lineno)d]'}
                          }
           }
