# coding: utf-8

import logging
import os

logger = logging
logger.basicConfig(
    handlers=[
        logging.FileHandler(
            filename=os.path.join(
                "D:",
                os.sep,
                "YandexDisk",
                "work",
                "facultetus",
                "app.log"
            ),
            encoding="utf-8",
            mode="a+",
        )
    ],
    format="%(asctime)s %(levelname)s --  %(name)s.%(funcName)s, %(lineno)d: %(message)s",
    datefmt="%Y-%m-%d, %H:%M:%S",
    level=logging.INFO,
)
