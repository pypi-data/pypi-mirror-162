


import os
import datetime
import typing
import json

from ..EnumLogLevel import EnumLogLevel






class Converter_compactJSON_to_raw(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def json_to_logEntry(self, jsonLogEntry:list) -> list:
		assert isinstance(jsonLogEntry, list)

		sType = jsonLogEntry[0]
		rawLogEntry = [
			sType,
			0,										# logEntryID
			0,										# indentationLevel
			0,										# parentLogEntryID
			jsonLogEntry[1],						# timeStamp
			EnumLogLevel.parse(jsonLogEntry[2]),	# logLevel
		]

		if rawLogEntry[0] == "txt":
			# nothing more to convert
			rawLogEntry.append(jsonLogEntry[3])
			assert len(rawLogEntry) == 7

		elif rawLogEntry[0] == "ex":
			# nothing more to convert
			rawLogEntry.append(jsonLogEntry[3])
			rawLogEntry.append(jsonLogEntry[4])
			rawLogEntry.append(jsonLogEntry[5])
			assert len(rawLogEntry) == 9

		elif rawLogEntry[0] == "desc":
			# convert list of nested elements
			rawLogEntry.append(jsonLogEntry[3])
			nested = []
			if jsonLogEntry[4] is not None:
				nested = [
					self.json_to_logEntry(x) for x in jsonLogEntry[4]
				]
			rawLogEntry.append(nested)

		else:
			raise Exception("Implementation Error!")

		return rawLogEntry
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

#







