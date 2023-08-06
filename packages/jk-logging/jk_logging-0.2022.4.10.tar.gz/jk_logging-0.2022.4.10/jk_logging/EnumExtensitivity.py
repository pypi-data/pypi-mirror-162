


import os

from enum import Enum







class EnumExtensitivity(Enum):

	VERY_SHORT = 0, 'veryShort'
	SHORTED = 10, 'shorted'
	FULL = 20, 'full'

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value_ = value
		member.fullname = name
		return member
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	#
	# Return an integer representation of this enumeration value.
	#
	def __int__(self):
		return self._value_
	#

	#
	# Return a string representation of this enumeration value.
	#
	def __str__(self):
		return self.fullname
	#

	#
	# Return a JSON compatible value for this enumeration value.
	#
	def toJSON(self):
		return self._value_
	#

	################################################################################################################################
	## Public Static Methods
	################################################################################################################################

	#
	# This method converts a string or integer representing a log level back to an enumeration instance.
	#
	@staticmethod
	def parse(data):
		if isinstance(data, EnumExtensitivity):
			return data

		if isinstance(data, int):
			return EnumExtensitivity.__dict__["_value2member_map_"][data]

		if isinstance(data, str):
			if data in EnumExtensitivity.__dict__["_member_names_"]:
				return EnumExtensitivity.__dict__[data]
			if data in ( "full", ):
				return EnumExtensitivity.FULL
			if data in ( "shortened", "short" ):
				return EnumExtensitivity.SHORTED
			if data in ( "veryShort", ):
				return EnumExtensitivity.VERY_SHORT

		raise Exception("Unrecognized extensitivity value: " + repr(data))
	#

#







