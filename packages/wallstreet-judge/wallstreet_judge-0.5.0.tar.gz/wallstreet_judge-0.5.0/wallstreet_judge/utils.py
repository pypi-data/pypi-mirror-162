import logging 

def get_logger(name:str, level: int = logging.INFO)->logging.Logger:
    logger = logging.getLogger(name=name)
    logger.setLevel(level=level)
    formatter = logging.Formatter("%(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger