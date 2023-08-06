

# from __future__ import annotations

import os
import typing

import jk_typing
import jk_utils
import jk_logging
import jk_json
import jk_prettyprintobj

from .BaseVersionConstraint import BaseVersionConstraint

from .VersionConstraintGE import VersionConstraintGE
from .VersionConstraintGT import VersionConstraintGT
from .VersionConstraintLE import VersionConstraintLE
from .VersionConstraintLT import VersionConstraintLT
from .VersionConstraintNE import VersionConstraintNE
from .VersionConstraintEQ import VersionConstraintEQ

from .VersionConstraintOR import VersionConstraintOR
from .VersionConstraintAND import VersionConstraintAND

from .Version import Version





class _ConstraintDeserializer(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	@staticmethod
	def __deserializeList(jData:list) -> list:
		if isinstance(jData, list):
			return [
				_ConstraintDeserializer.deserialize(x) for x in jData
			]
		else:
			raise Exception("Invalid data format!")
	#

	@staticmethod
	def __deserializeVersion(jData:str) -> Version:
		if isinstance(jData, str):
			return Version(jData)
		else:
			raise Exception("Invalid data format!")
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	@staticmethod
	def deserialize(jData:typing.Union[tuple,list]) -> BaseVersionConstraint:
		if isinstance(jData, (tuple,list)) and (len(jData) == 2):
			op, opData = jData
			if op == "and":
				return VersionConstraintAND(*_ConstraintDeserializer.__deserializeList(opData))
			elif op == "or":
				return VersionConstraintOR(*_ConstraintDeserializer.__deserializeList(opData))
			elif op == "==":
				return VersionConstraintEQ(_ConstraintDeserializer.__deserializeVersion(opData))
			elif op == "!=":
				return VersionConstraintNE(_ConstraintDeserializer.__deserializeVersion(opData))
			elif op == ">":
				return VersionConstraintGT(_ConstraintDeserializer.__deserializeVersion(opData))
			elif op == ">=":
				return VersionConstraintGE(_ConstraintDeserializer.__deserializeVersion(opData))
			elif op == "<":
				return VersionConstraintLT(_ConstraintDeserializer.__deserializeVersion(opData))
			elif op == "<=":
				return VersionConstraintLE(_ConstraintDeserializer.__deserializeVersion(opData))
			else:
				raise Exception("Invalid data format!")
		else:
			raise Exception("Invalid data format!")
	#

#

def deserializeConstraint(jData:typing.Union[tuple,list]) -> BaseVersionConstraint:
	return _ConstraintDeserializer.deserialize(jData)
#




