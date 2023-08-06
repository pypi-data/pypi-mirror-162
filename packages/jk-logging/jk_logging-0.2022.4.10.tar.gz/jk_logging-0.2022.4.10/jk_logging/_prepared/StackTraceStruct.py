

import os
import typing
import collections





class StackTraceStruct:

	__slots__ = (
		"_filePath",
		"_lineNo",
		"_moduleName",
		"_sourceCode",
	)

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self,
			filePath:str,
			lineNo:int,
			moduleName:str,
			sourceCode:str
		):

		self._filePath = filePath
		self._lineNo = lineNo
		self._moduleName = moduleName
		self._sourceCode = sourceCode
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	@property
	def filePath(self) -> str:
		return self._filePath
	#

	@property
	def lineNo(self) -> int:
		return self._lineNo
	#

	@property
	def moduleName(self) -> str:
		return self._moduleName
	#

	@property
	def sourceCode(self) -> str:
		return self._sourceCode
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def toJSONPretty(self) -> dict:
		return {
			"file": self._filePath,
			"line": self._lineNo,
			"module": self._moduleName,
			"sourcecode": self._sourceCode,
		}
	#

	def toJSON(self) -> tuple:
		return (
			self._filePath,
			self._lineNo,
			self._moduleName,
			self._sourceCode,
		)
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

	@staticmethod
	def fromJSONAny(data):
		if isinstance(data, StackTraceStruct):
			return data

		if isinstance(data, dict):
			return StackTraceStruct(
				data["file"],
				data["line"],
				data["module"],
				data["sourcecode"],
			)

		if isinstance(data, (list,tuple)):
			assert len(data) == 4
			return StackTraceStruct(
				data[0],
				data[1],
				data[2],
				data[3],
			)
		
		raise TypeError("Data is of type " + type(data))
	#

	@staticmethod
	def fromJSONPretty(data):
		#if isinstance(data, StackTraceStruct):
		#	return data

		if isinstance(data, dict):
			return StackTraceStruct(
				data["file"],
				data["line"],
				data["module"],
				data["sourcecode"],
			)

		raise TypeError("Data is of type " + type(data))
	#

	@staticmethod
	def fromJSON(data):
		if isinstance(data, (list,tuple)):
			assert len(data) == 4
			return StackTraceStruct(
				data[0],
				data[1],
				data[2],
				data[3],
			)

		raise TypeError("Data is of type " + type(data))
	#

#




