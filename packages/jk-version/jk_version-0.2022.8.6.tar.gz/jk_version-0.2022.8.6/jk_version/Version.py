

# from __future__ import annotations

import typing
import re
import datetime











class Version(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor
	#
	# @param		int[]|str version				The version string this object should represent
	#
	def __init__(self, version:typing.Union[str,list,tuple,dict] = "0", *, _epoch:int = 0, _extra:str = None):
		assert isinstance(_epoch, int)
		if _extra is not None:
			assert isinstance(_extra, str)

		self.__epoch = _epoch
		self.__extra = _extra

		if isinstance(version, str):

			self.__numbers, self.__epoch, self.__extra = Version.__parseFromStr(version, False)
			if self.__numbers is None:
				raise Exception("Failed to parse version string: \"" + version + "\"")
			for i in self.__numbers:
				assert isinstance(i, int)
			assert isinstance(self.__epoch, int)
			if _extra is not None:
				assert isinstance(_extra, str)

		elif isinstance(version, (list, tuple)):

			if len(version) == 0:
				raise Exception("Invalid version number: \"" + str(version) + "\"")

			for i in version:
				assert isinstance(i, int)

			self.__numbers = tuple(version)

		elif isinstance(version, dict):

			self.__epoch = version.get("epoch", 0)
			self.__numbers = tuple(version["numbers"])
			self.__extra = version.get("extra", None)

			self.__checkIfValid(version)

		else:
			raise Exception("Specified value is of invalid type: " + str(type(version)))
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def epoch(self) -> int:
		return self.__epoch
	#

	@property
	def extra(self) -> typing.Union[str,None]:
		return self.__extra
	#

	@property
	def length(self) -> int:
		return len(self.__numbers)
	#

	@property
	def numbers(self) -> list:
		return list(self.__numbers)
	#

	# TODO: rename to "isDateBased"
	@property
	def isDateBase(self) -> bool:
		if len(self.__numbers) < 4:
			return False
		if self.__numbers[0] != 0:
			return False
		if (self.__numbers[1] < 2010) or (self.__numbers[1] > 2100):
			return False
		if (self.__numbers[2] < 1) or (self.__numbers[2] > 12):
			return False
		if (self.__numbers[3] < 1) or (self.__numbers[3] > 31):
			return False

		# everything seems to be plausible.

		return True
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def __checkIfValid(self, original):
		if len(self.__numbers) == 0:
			raise Exception("Invalid version number: " + repr(original))

		for i in self.__numbers:
			if not isinstance(i, int):
				raise Exception("Invalid version number: " + repr(original))

		if self.__extra is not None:
			if not isinstance(self.__extra, str):
				raise Exception("Invalid version number: " + repr(original))

		if not isinstance(self.__epoch, int):
			raise Exception("Invalid version number: " + repr(original))
	#

	@staticmethod
	def __parseFromStr(text:str, bStrict:bool = False) -> tuple:
		try:
			m = re.match(r"^((?P<epoch>[0-9]+):)?(?P<version>[0-9\.]+)([\-~\+](?P<extra>.+))?$", text)
			if not bStrict:
				if not m:
					m = re.match(r"^((?P<epoch>[0-9]+):)?(?P<version>[0-9\.]+)([\-~\+\.](?P<extra>[a-zA-Z][a-zA-Z0-9]*))?$", text)
			if not m:
				return None, None, None

			_epoch = 0
			_extra = None

			sEpoch = m.group("epoch")
			sVersion = m.group("version")
			sExtra = m.group("extra")
			if sEpoch:
				_epoch = int(sEpoch)
			if sExtra:
				_extra = sExtra

			# parse regular version number

			numbers = []
			for sVPart in sVersion.split("."):
				while (len(sVPart) > 1) and (sVPart[0] == "0"):		# remove trailing zeros of individual version components to allow accidental specification of dates as version information
					sVPart = sVPart[1:]
				numbers.append(int(sVPart))

			# ----

			_numbers = tuple(numbers)
			# print(">>>>", repr(text), repr(_numbers), repr(_epoch), repr(_extra))
			return _numbers, _epoch, _extra

		except Exception as ee:
			return None, None, None
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def clone(self):	# -> Version:
		return Version(self.__numbers, _epoch=self.__epoch, _extra=self.__extra)
	#

	def __hash__(self):
		return hash(self.__numbers)
	#

	def __str__(self):
		if (self.__epoch is None) or (self.__epoch == 0):
			ret = ""
		else:
			ret = str(self.__epoch) + ":"

		bFirst = True
		for v in self.__numbers:
			if bFirst:
				bFirst = False
			else:
				ret += "."
			ret += str(v)

		if self.__extra:
			ret += "-" + self.__extra

		return ret
	#

	def __repr__(self):
		return self.__str__()
	#

	def compareTo(self, other):
		if isinstance(other, str):
			other = Version(other)

		if isinstance(other, Version):
			aNumbers = [ self.__epoch ]
			aNumbers.extend(self.__numbers)
			bNumbers = [ other.__epoch ]
			bNumbers.extend(other.__numbers)

			maxLength = max(len(aNumbers), len(bNumbers))

			while len(aNumbers) < maxLength:
				aNumbers.append(0)
			while len(bNumbers) < maxLength:
				bNumbers.append(0)

			# print("aNumbers", aNumbers)
			# print("bNumbers", bNumbers)

			for i in range(0, maxLength):
				na = aNumbers[i]
				nb = bNumbers[i]
				x = (na > nb) - (na < nb)
				# print("> " + str(na) + "  " + str(nb) + "  " + str(x))
				if x != 0:
					return x
			return 0

		else:
			raise Exception("Incompatible types: 'Version' and " + repr(type(other).__name__))
	#

	def __cmp__(self, other):
		n = self.compareTo(other)
		return n
	#

	def __lt__(self, other):
		n = self.compareTo(other)
		#print "???? a=" + str(self)
		#print "???? b=" + str(other)
		#print "???? " + str(n)
		return n < 0
	#

	def __le__(self, other):
		n = self.compareTo(other)
		#print "???? a=" + str(self)
		#print "???? b=" + str(other)
		#print "???? " + str(n)
		return n <= 0
	#

	def __gt__(self, other):
		n = self.compareTo(other)
		return n > 0
	#

	def __ge__(self, other):
		n = self.compareTo(other)
		return n >= 0
	#

	def __eq__(self, other):
		n = self.compareTo(other)
		return n == 0
	#

	def __ne__(self, other):
		n = self.compareTo(other)
		return n != 0
	#

	def toJSON(self) -> dict:
		return {
			"epoch": self.__epoch,
			"numbers": self.__numbers,
			"extra": self.__extra,
		}
	#

	def dump(self):
		print("Version<(")
		print("\tepoch=" + repr(self.__epoch))
		print("\tnumbers=" + repr(self.__numbers))
		print("\textra=" + repr(self.__extra))
		print(")>")
	#

	@staticmethod
	def now():
		dt = datetime.datetime.now()
		return Version([ 0, dt.year, dt.month, dt.day ])
	#

	@staticmethod
	def fromTimeStamp(t):
		dt = datetime.datetime.fromtimestamp(t)
		return Version([ 0, dt.year, dt.month, dt.day ])
	#

	@staticmethod
	def parseFromStr(text:str, bStrict:bool = False):
		_numbers, _epoch, _extra = Version.__parseFromStr(text, bStrict)
		if _numbers is None:
			raise Exception("Failed to parse version string: \"" + text + "\"")

		return Version(_numbers, _epoch=_epoch, _extra=_extra)
	#

#
