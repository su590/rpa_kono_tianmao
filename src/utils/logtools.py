# -*- coding: utf-8 -*-
"""
基于logging的日志工具库
"""
import datetime
import logging
import os


class _LogTools:

    def __init__(self):
        self._fmt: str = '%(asctime)s %(levelname)s %(name)s: %(message)s'
        self._level: int = logging.DEBUG

    def colorlog(
            self,
            logger: logging.Logger = None,
            fmt: str = None,
            level: int = None,
            length: dict[str, int] = None,
    ) -> None:
        """
        新增一个StreamHandler输出(即控制台输出),使其多彩化
        需要注意，使用前提是安装了第三方库colorlog
        :param logger: 指定日志器，默认根日志器
        :param fmt: 指定日志格式
        :param level: 指定日志级别
        :param length: 指定日志格式中每一项的长度，目前支持的日志项=[%(name)s,%(levelname)s,%(thread)d]
        """
        if fmt is None:
            fmt = self._fmt
        if level is None:
            level = self._level

        import colorlog

        class CustomColoredFormatter(colorlog.ColoredFormatter):
            _LENGTH = length

            def format(self, record):
                log_message = super().format(record)

                if self._LENGTH is None:
                    return log_message

                # 自定义 %(name)s 的长度
                if (size := self._LENGTH.get('%(name)s')) is not None:
                    name = record.name.ljust(size)
                    log_message = log_message.replace(record.name, name)
                # 自定义 %(levelname)s 的长度
                if (size := self._LENGTH.get('%(levelname)s')) is not None:
                    levelname = record.levelname.ljust(size)  # 用空格补充到最大宽度
                    log_message = log_message.replace(record.levelname, levelname)
                # 自定义 %(thread)d 的长度
                if (size := self._LENGTH.get('%(thread)d')) is not None:
                    record.thread = f"{record.thread:<{size}}"

                return log_message

        logger = logger or logging.getLogger()
        streamhdlr = colorlog.StreamHandler()
        streamhdlr.setLevel(level)
        logger.addHandler(streamhdlr)
        streamhdlr.setFormatter(CustomColoredFormatter(
            f'%(log_color)s{fmt}',
            log_colors={
                'DEBUG': 'bold,green',
                'INFO': 'bold,blue',
                'WARNING': 'bold,yellow',
                'ERROR': 'bold,red',
                'CRITICAL': 'bold,red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        ))

    def dailylog(
            self,
            logger: logging.Logger = None,
            datefmt: str = None,
            folder: str = None,
            fmt: str = None,
            level: int = None,
            length: dict[str, int] = None,
    ) -> None:
        """
        按日缓存到日志文件中
        :param logger: 指定日志器，默认根日志器
        :param datefmt: 指定日期格式
        :param folder: 指定缓存文件夹位置
        :param fmt: 指定日志格式
        :param level: 指定日志级别
        :param length: 指定日志格式中每一项的长度，目前支持的日志项=[%(name)s,%(levelname)s,%(thread)d]
        """
        if datefmt is None:
            datefmt = '%Y_%m_%d'
        if fmt is None:
            fmt = self._fmt
        if level is None:
            level = self._level
        if folder is None:
            folder = './'

        class DailyFileHandler(logging.FileHandler):
            """
            按日实时文件名的文件日志器
            每次日期记录时都将对比实时的新文件名是否与已有文件名相同，不同时将刷新缓存，并更改当前文件名，然后启用新文件名进行日志缓存
            """

            def __init__(self, *args, **kwargs):
                kwargs['encoding'] = 'utf-8'
                super().__init__(*args, **kwargs)
                self._custom_datefmt = datefmt
                self._custom_folder = folder

            def emit(self, record: logging.LogRecord) -> None:
                # new_filename = os.path.join(self._custom_folder,
                #                             f'{datetime.date.today().strftime(self._custom_datefmt)}.log')
                # if self.baseFilename != new_filename:
                #     self.stream.flush()
                #     self.stream.close()
                #     setattr(self, 'stream', None)
                #     self.baseFilename = new_filename
                # super().emit(record)
                new_filename = os.path.join(self._custom_folder,
                                            f'{datetime.date.today().strftime(self._custom_datefmt)}.log')
                if self.baseFilename != new_filename:
                    self.stream.flush()
                    self.stream.close()
                    self.baseFilename = new_filename
                    self.stream = open(self.baseFilename, 'a', encoding='utf-8')
                super().emit(record)

        class CustomFormatter(logging.Formatter):
            _LENGTH = length

            def format(self, record):
                log_message = super().format(record)

                if self._LENGTH is None:
                    return log_message

                # 自定义 %(name)s 的长度
                if (size := self._LENGTH.get('%(name)s')) is not None:
                    name = record.name.ljust(size)
                    log_message = log_message.replace(record.name, name)
                # 自定义 %(levelname)s 的长度
                if (size := self._LENGTH.get('%(levelname)s')) is not None:
                    levelname = record.levelname.ljust(size)  # 用空格补充到最大宽度
                    log_message = log_message.replace(record.levelname, levelname)
                # 自定义 %(thread)d 的长度
                if (size := self._LENGTH.get('%(thread)d')) is not None:
                    record.thread = f"{record.thread:<{size}}"

                return log_message

        logger = logger or logging.getLogger()
        handler = DailyFileHandler(os.path.join(folder, f'{datetime.date.today().strftime(datefmt)}.log'))
        handler.setFormatter(CustomFormatter(fmt))
        handler.setLevel(level)
        logger.addHandler(handler)


logtools = LogTools = _LogTools()
