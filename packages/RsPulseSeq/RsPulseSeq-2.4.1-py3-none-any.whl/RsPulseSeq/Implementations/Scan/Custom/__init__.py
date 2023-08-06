from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Custom:
	"""Custom commands group definition. 13 total commands, 2 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("custom", core, parent)

	@property
	def entry(self):
		"""entry commands group. 1 Sub-classes, 10 commands."""
		if not hasattr(self, '_entry'):
			from .Entry import Entry
			self._entry = Entry(self._core, self._cmd_group)
		return self._entry

	@property
	def importPy(self):
		"""importPy commands group. 1 Sub-classes, 1 commands."""
		if not hasattr(self, '_importPy'):
			from .ImportPy import ImportPy
			self._importPy = ImportPy(self._core, self._cmd_group)
		return self._importPy

	def clone(self) -> 'Custom':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Custom(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
