


from enum import Enum
import typing
import re
import sys

from jk_logging.fmt.DefaultTimeStampFormatter import DefaultTimeStampFormatter

from .impl.IDCounter import IDCounter

from .EnumLogLevel import EnumLogLevel
from .AbstractLogger import AbstractLogger
from .BufferLogger import BufferLogger
from .ConsoleLogger import ConsoleLogger
from .DetectionLogger_v0 import DetectionLogger_v0
from .DetectionLogger import DetectionLogger
from .FilterLogger import FilterLogger
from .MulticastLogger import MulticastLogger
from .NamedMulticastLogger import NamedMulticastLogger
from .NullLogger import NullLogger
#from .SimpleFileLogger import SimpleFileLogger
from .FileLogger import FileLogger
from .StringListLogger import StringListLogger
from .JSONFileLogger import JSONFileLogger
from .EnumExtensitivity import EnumExtensitivity

from .fmt.AbstractLogMessageFormatter import AbstractLogMessageFormatter
from .fmt.LogMessageFormatter import LogMessageFormatter
from .fmt.ColoredLogMessageFormatter import ColoredLogMessageFormatter
from .fmt.HTMLLogMessageFormatter import HTMLLogMessageFormatter
from .fmt.DefaultTimeStampFormatter import DefaultTimeStampFormatter

from .debugging.DebugTimeStampFormatter import DebugTimeStampFormatter






class _Instantiator:

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self) -> None:
		self.__logMsgFormatterCache = {}

		#self.__logMsgFormatterCache[self.__createLogMsgFormatterSignature("color", COLOR_LOG_MESSAGE_FORMATTER.outputMode)] = COLOR_LOG_MESSAGE_FORMATTER
		#self.__logMsgFormatterCache[self.__createLogMsgFormatterSignature("color", COLOR_LOG_MESSAGE_FORMATTER.outputMode)] = COLOR_LOG_MESSAGE_FORMATTER
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def __createLogMsgFormatterSignature(self,
			sLogMsgFormatterType:str,
			sExtensitivity:typing.Union[str,EnumExtensitivity,int],
			sTimeStampFormatter:str,
		) -> str:

		assert isinstance(sLogMsgFormatterType, str)
		assert sLogMsgFormatterType
		assert isinstance(sExtensitivity, (str, int, EnumExtensitivity))
		assert isinstance(sTimeStampFormatter, str)

		sExtensitivity = str(EnumExtensitivity.parse(sExtensitivity))
		return "FMTTR-{}-{}".format(sLogMsgFormatterType, sExtensitivity)
	#

	#
	# @param		str logMsgFormatterType		The log message formatter type: "default", "color" or "html"
	#
	def __newLogMsgFormatter(self,
			sLogMsgFormatterType:str,
			sExtensitivity:typing.Union[str,None],
			sTimeStampFormatter:typing.Union[str,None],
		) -> AbstractLogMessageFormatter:

		extensitivity = EnumExtensitivity.parse(sExtensitivity) if sExtensitivity else None

		timeStampFormatter = None if sTimeStampFormatter is None else self.__newTimeStampFormatter(sTimeStampFormatter)

		if sLogMsgFormatterType == "default":
			# NOTE: ignore extensitivity for now as this feature is not yet fully implemented
			return LogMessageFormatter(timeStampFormatter=timeStampFormatter)

		elif sLogMsgFormatterType == "color":
			return ColoredLogMessageFormatter(extensitivity=extensitivity, timeStampFormatter=timeStampFormatter)

		elif sLogMsgFormatterType == "html":
			return HTMLLogMessageFormatter(extensitivity=extensitivity, timeStampFormatter=timeStampFormatter)

		else:
			raise Exception("Unknown log message formatter: " + repr(sLogMsgFormatterType))
	#

	#
	# @param		str sName		The timestamp formatter type: "default", "debug"
	#
	def __newTimeStampFormatter(self, sName:str) -> typing.Callable[[float],typing.Any]:
		if sName == "default":
			return DefaultTimeStampFormatter()

		if sName == "debug":
			return DebugTimeStampFormatter()

		else:
			raise Exception("Unknown timestamp formatter: " + repr(sName))
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def instantiateLogMsgFormatter(self, cfg:typing.Union[str,dict]):
		sExtensitivity = "full"
		sTimeStampFormatter = "default"

		if isinstance(cfg, dict):
			sLogMsgFormatterType = cfg["type"]
			sExtensitivity = cfg.get("extensitivity", "full")
			sTimeStampFormatter = cfg.get("timeStampFormatter", "default")

		elif isinstance(cfg, str):
			sLogMsgFormatterType = cfg

		else:
			raise Exception("Invalid configuration data specified for creating a log message formatter!")

		_signature = self.__createLogMsgFormatterSignature(sLogMsgFormatterType, sExtensitivity, sTimeStampFormatter)

		if _signature not in self.__logMsgFormatterCache:
			self.__logMsgFormatterCache[_signature] = self.__newLogMsgFormatter(sLogMsgFormatterType, sExtensitivity, sTimeStampFormatter)

		return self.__logMsgFormatterCache[_signature]
	#

#

_INSTANTIATOR = _Instantiator()








#
# @param		dict|str cfg			Information about the log message formatter required.
#										If the specified value is "default", "color", "html", one of the default
#										log message formatter instances is returned.
#										If the specified value is a dictionary it can/must have the following key value pairs:
#										* `str type` : The type of the log message formatter to created, either  "default", "color" or "html"
#										* `str extensitivity` : How talkative should the formatter be? Specify either
#											"full", "short" (alternatives: "shorted", shortened") or "veryShort".
#
def instantiateLogMsgFormatter(cfg:typing.Union[str,dict,None]):
	if cfg is None:
		return None
	return _INSTANTIATOR.instantiateLogMsgFormatter(cfg)
#



def instantiate(cfg):
	logMsgFormatter = instantiateLogMsgFormatter(cfg.get("logMsgFormatter"))

	loggerType = cfg["type"]

	if loggerType == "BufferLogger":
		if logMsgFormatter:
			raise Exception("Loggers of type BufferLogger do not have a log message formatter!")
		return BufferLogger.create()

	elif loggerType == "ConsoleLogger":
		return ConsoleLogger.create(
			logMsgFormatter = logMsgFormatter
		)

	elif loggerType == "DetectionLogger_v0":
		if logMsgFormatter:
			raise Exception("Loggers of type DetectionLogger_v0 do not have a log message formatter!")
		return DetectionLogger_v0.create(logger=instantiate(cfg["nested"]))

	elif loggerType == "DetectionLogger":
		if logMsgFormatter:
			raise Exception("Loggers of type DetectionLogger do not have a log message formatter!")
		return DetectionLogger.create(logger=instantiate(cfg["nested"]))

	elif loggerType == "FilterLogger":
		if logMsgFormatter:
			raise Exception("Loggers of type FilterLogger do not have a log message formatter!")
		if "minLogLevel" in cfg:
			logLevel = EnumLogLevel.parse(cfg["minLogLevel"])
		else:
			logLevel = EnumLogLevel.WARNING
		return FilterLogger.create(logger=instantiate(cfg["nested"]), minLogLevel = logLevel)

	elif loggerType == "MulticastLogger":
		if logMsgFormatter:
			raise Exception("Loggers of type MulticastLogger do not have a log message formatter!")
		loggers = []
		for item in cfg["nested"]:
			loggers.append(instantiate(item))
		return MulticastLogger.create(*loggers)

	elif loggerType == "NamedMulticastLogger":
		if logMsgFormatter:
			raise Exception("Loggers of type NamedMulticastLogger do not have a log message formatter!")
		loggers = {}
		for itemKey in cfg["nested"]:
			loggers[itemKey] = instantiate(cfg["nested"][itemKey])
		return NamedMulticastLogger.create(**loggers)

	elif loggerType == "NullLogger":
		if logMsgFormatter:
			raise Exception("Loggers of type NullLogger do not have a log message formatter!")
		return NullLogger.create()

	elif loggerType == "SimpleFileLogger":
		raise Exception("Not supported: SimpleFileLogger")

	elif loggerType == "FileLogger":
		fileMode = cfg.get("fileMode", None)
		if fileMode != None:
			if isinstance(fileMode, int):
				fileMode = str(fileMode)
			if isinstance(fileMode, str):
				if re.match("^[0-7][0-7][0-7]$", fileMode):
					fileMode = int(fileMode, 8)
				else:
					raise Exception("Invalid mode specified for file logger!")
			else:
				raise Exception("Invalid mode specified for file logger!")

		return FileLogger.create(
			filePath = cfg["filePath"],
			rollOver = cfg.get("rollOver", None),
			bAppendToExistingFile = cfg.get("bAppendToExistingFile", cfg.get("appendToExistingFile", True)),
			bFlushAfterEveryLogMessage = cfg.get("bFlushAfterEveryLogMessage", cfg.get("flushAfterEveryLogMessage", True)),
			fileMode = fileMode,
			logMsgFormatter = logMsgFormatter,
		)

	elif loggerType == "StringListLogger":
		return StringListLogger.create(
			logMsgFormatter = logMsgFormatter
		)

	elif loggerType == "JSONFileLogger":
		if logMsgFormatter:
			raise Exception("Loggers of type JSONFileLogger do not have a log message formatter!")
		return JSONFileLogger.create(cfg["filePath"])

	else:
		raise Exception("Unknown logger type: " + loggerType)
#














