

# from __future__ import annotations

import re
import os
import typing

from .Version import Version
from .BaseVersionConstraint import BaseVersionConstraint




class VersionConstraintOR(BaseVersionConstraint):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, *elements):
		for c in elements:
			assert isinstance(c, BaseVersionConstraint)
		self.__elements = elements
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def elements(self) -> typing.Tuple[BaseVersionConstraint]:
		return self.__elements
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def check(self, version:Version) -> bool:
		assert isinstance(version, Version)

		for c in self.__elements:
			if c.check(version):
				return True
		return False
	#

	def toJSON(self) -> list:
		return [ "or", [
			x.toJSON() for x in self.__elements
		] ]
	#

	def simplify(self) -> BaseVersionConstraint:
		ret = []
		for x in self.__elements:
			x = x.simplify()
			if isinstance(x, VersionConstraintOR):
				ret.extend(x.elements)
			else:
				ret.append(x)

		if len(ret) == 1:
			return ret[0]
		else:
			return VersionConstraintOR(*ret)
	#

	def __str__(self):
		return "(" + (" || ".join([ str(x) for x in self.__elements ])).strip() + ")"
	#

	def __repr__(self):
		return "(" + (" || ".join([ str(x) for x in self.__elements ])).strip() + ")"
	#

#






