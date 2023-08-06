

import os
import typing
import datetime





from .StackTraceStructList import StackTraceStructList
#from .LogEntryStructList import LogEntryStructList





class LogEntryStruct:

	__slots__ = (
		"_sType",					# str "desc", "txt", "ex"
		"_logEntryID",				# int
		"_indentationLevel",		# int
		"_parentLogEntryID",		# int|None
		"_timeStamp",				# float
		"_logLevel",				# EnumLogLevel
		"_logMsg",					# str
		"_exClass",					# str
		"_exMsg",					# str
		"_exStackTrace",			# StackTraceStructList
		"_nestedList",				# LogEntryStructList
	)

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self,
			sType:str,
			logEntryID:int,
			indentationLevel:str,
			parentLogEntryID:str,
			timeStamp:float,
			logLevel:str,
			logMsg:str,
			exClass:str,
			exMsg:str,
			exStackTrace:StackTraceStructList,
			nestedList:list,		# LogEntryStructList
		):

		self._sType = sType
		self._logEntryID = logEntryID
		self._indentationLevel = indentationLevel
		self._parentLogEntryID = parentLogEntryID
		self._timeStamp = timeStamp
		self._logLevel = logLevel
		self._logMsg = logMsg
		self._exClass = exClass
		self._exMsg = exMsg
		self._exStackTrace = exStackTrace
		self._nestedList = nestedList
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	@property
	def sType(self) -> str:
		return self._sType
	#

	@property
	def logEntryID(self) -> int:
		return self._logEntryID
	#

	@property
	def indentationLevel(self) -> str:
		return self._indentationLevel
	#

	@property
	def parentLogEntryID(self) -> str:
		return self._parentLogEntryID
	#

	@property
	def timeStamp(self) -> float:
		return self._timeStamp
	#

	@property
	def logLevel(self) -> str:
		return self._logLevel
	#

	@property
	def logMsg(self) -> str:
		return self._logMsg
	#

	@property
	def exClass(self) -> str:
		return self._exClass
	#

	@property
	def exMsg(self) -> str:
		return self._exMsg
	#

	@property
	def exStackTrace(self) -> StackTraceStructList:
		return self._exStackTrace
	#

	@property
	def nestedList(self) -> list:				# LogEntryStructList
		return self._nestedList
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	@staticmethod
	def __timeStamp_to_prettyJSONDict(t:float) -> dict:
		assert isinstance(t, (int,float))
		t = datetime.datetime.fromtimestamp(t)
		return {
			"t": t,
			"year": t.year,
			"month": t.month,
			"day": t.day,
			"hour": t.hour,
			"minute": t.minute,
			"second": t.second,
			"ms": t.microsecond // 1000,
			"us": t.microsecond % 1000,
		}
	#

	@staticmethod
	def __prettyJSONDict_to_timeStamp(jData:dict) -> float:
		assert isinstance(jData, dict)
		t = jData["t"]
		assert isinstance(t, (int,float))
		return t
	#

	@staticmethod
	def __jsonToTimeStamp(jData:typing.Union[float,dict]) -> float:
		if isinstance(jData, float):
			return jData

		assert isinstance(jData, dict)
		t = jData["t"]
		assert isinstance(t, (int,float))
		return t
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def toJSONPretty(self) -> dict:
		ret = {
			"type": self._sType,
			"id": self._logEntryID,
			"parentID": self._parentLogEntryID,
			"indent": self._indentationLevel,
			"timeStamp": self.__timeStamp_to_prettyJSONDict(self._timeStamp),
			"logLevel": str(self._logLevel),
			"logLevelN": int(self._logLevel),
		}

		if self._sType == "txt":
			ret["text"] = self._logMsg
		elif self._sType == "ex":
			ret["exception"] = self._exClass
			ret["text"] = self._exMsg
			ret["stacktrace"] = self._exStackTrace.toJSONPretty() if self._exStackTrace else None
		elif self._sType == "desc":
			ret["text"] = self._logMsg
			ret["children"] = self._nestedList.toJSONPretty()
		else:
			raise Exception("Implementation Error!")

		return ret
	#

	def toJSON(self) -> tuple:
		ret = []

		if self._sType == "txt":
			return [
				"txt",
				self._logEntryID,
				self._indentationLevel,
				self._parentLogEntryID,
				self._timeStamp,
				int(self._logLevel),
				self._logMsg,
			]
		elif self._sType == "ex":
			return [
				"ex",
				self._logEntryID,
				self._indentationLevel,
				self._parentLogEntryID,
				self._timeStamp,
				int(self._logLevel),
				self._exClass,
				self._exMsg,
				self._exStackTrace.toJSON(),
			]
		elif self._sType == "desc":
			return [
				"desc",
				self._logEntryID,
				self._indentationLevel,
				self._parentLogEntryID,
				self._timeStamp,
				int(self._logLevel),
				self._logMsg,
				self._nestedList.toJSON(),
			]
		else:
			raise Exception("Implementation Error!")
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

	@staticmethod
	def fromJSONAny(data:typing.Union[dict,list,tuple]):
		if isinstance(data, LogEntryStruct):
			return data

		if isinstance(data, dict):
			sType = data["type"]
			if sType == "txt":
				# 7 entries
				return LogEntryStruct(
					sType = data["type"],
					logEntryID = data["id"],
					indentationLevel = data["indent"],
					parentLogEntryID = data["parentID"],
					timeStamp = LogEntryStruct.__jsonToTimeStamp(data["timeStamp"]),
					logLevel = data["logLevelN"],
					logMsg = data["text"],
					exClass = None,
					exMsg = None,
					exStackTrace = None,
					nestedList = None,
				)
			elif sType == "ex":
				# 9 entries
				return LogEntryStruct(
					sType = data["type"],
					logEntryID = data["id"],
					indentationLevel = data["indent"],
					parentLogEntryID = data["parentID"],
					timeStamp = LogEntryStruct.__jsonToTimeStamp(data["timeStamp"]),
					logLevel = data["logLevelN"],
					logMsg = None,
					exClass = data["exception"],
					exMsg = data["text"],
					exStackTrace = StackTraceStructList.fromJSONAny(data["stacktrace"]),
					nestedList = None,
				)
			elif sType == "desc":
				# 8 entries
				return LogEntryStruct(
					sType = data["type"],
					logEntryID = data["id"],
					indentationLevel = data["indent"],
					parentLogEntryID = data["parentID"],
					timeStamp = LogEntryStruct.__jsonToTimeStamp(data["timeStamp"]),
					logLevel = data["logLevelN"],
					logMsg = data["text"],
					exClass = None,
					exMsg = None,
					exStackTrace = None,
					nestedList = LogEntryStructList.fromJSONAny(data["children"]),
				)
			else:
				raise Exception("Data Error!")

		if isinstance(data, (list,tuple)):
			sType = data[0]
			logEntryID = data[1]
			indent = data[2]
			parentID = data[3]
			timeStamp = LogEntryStruct.__jsonToTimeStamp(data[4])
			logLevelN = data[5]
			if sType == "txt":
				assert len(data) == 7
				# 7 entries
				return LogEntryStruct(
					sType = sType,
					logEntryID = logEntryID,
					indentationLevel = indent,
					parentLogEntryID = parentID,
					timeStamp = timeStamp,
					logLevel = logLevelN,
					logMsg = data[6],
					exClass = None,
					exMsg = None,
					exStackTrace = None,
					nestedList = None,
				)
			elif sType == "ex":
				assert len(data) == 9
				# 9 entries
				return LogEntryStruct(
					sType = sType,
					logEntryID = logEntryID,
					indentationLevel = indent,
					parentLogEntryID = parentID,
					timeStamp = timeStamp,
					logLevel = logLevelN,
					logMsg = None,
					exClass = data[6],
					exMsg = data[7],
					exStackTrace = StackTraceStructList.fromJSONAny(data[8]),
					nestedList = None,
				)
			elif sType == "desc":
				assert len(data) == 8
				# 8 entries
				return LogEntryStruct(
					sType = sType,
					logEntryID = logEntryID,
					indentationLevel = indent,
					parentLogEntryID = parentID,
					timeStamp = timeStamp,
					logLevel = logLevelN,
					logMsg = data[6],
					exClass = None,
					exMsg = None,
					exStackTrace = None,
					nestedList = LogEntryStructList.fromJSONAny(data[7]),
				)
			else:
				raise Exception("Data Error!")
		
		raise TypeError("Data is of type " + type(data))
	#

#






class LogEntryStructList(list):

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructor
	################################################################################################################################

	################################################################################################################################
	## Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def toJSONPretty(self) -> dict:
		ret = []
		for x in self:
			assert isinstance(x, LogEntryStruct)
			ret.append(x.toJSONPretty())
		return ret
	#

	def toJSON(self) -> list:
		ret = []
		for x in self:
			assert isinstance(x, LogEntryStruct)
			ret.append(x.toJSON())
		return ret
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

	@staticmethod
	def fromJSONAny(data:typing.Union[list,tuple]):
		assert isinstance(data, (list, tuple))

		return [
			LogEntryStruct.fromJSONAny(x) for x in data
		]
	#

#



