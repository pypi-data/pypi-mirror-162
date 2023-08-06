

# from __future__ import annotations

import re
import os
import typing

from .Version import Version
from .BaseVersionConstraint import BaseVersionConstraint




class VersionConstraintAND(BaseVersionConstraint):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, *elements):
		for c in elements:
			assert isinstance(c, BaseVersionConstraint)
		assert elements			# no constraint can be satisfied!

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
			if not c.check(version):
				return False
		return True
	#

	def toJSON(self) -> list:
		return [ "and", [
			x.toJSON() for x in self.__elements
		] ]
	#

	def simplify(self) -> BaseVersionConstraint:
		ret = []
		for x in self.__elements:
			x = x.simplify()
			if isinstance(x, VersionConstraintAND):
				ret.extend(x.elements)
			else:
				ret.append(x)

		if len(ret) == 1:
			return ret[0]
		else:
			return VersionConstraintAND(*ret)
	#

	def __str__(self):
		return "(" + (" ".join([ str(x) for x in self.__elements ])).strip() + ")"
	#

	def __repr__(self):
		return "(" + (" ".join([ str(x) for x in self.__elements ])).strip() + ")"
	#

#






