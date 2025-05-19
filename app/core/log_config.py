LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s  - %(message)s",
        },
        "access": {
            "format": "[%(asctime)s] %(levelname)s  - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "uvicorn.error": {
            "level": "DEBUG",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "DEBUG",
            "handlers": ["access"],
            "propagate": False,
        },
        "app": {
            "handlers": ["default"],
            "level": "DEBUG",
        },
    },
}
