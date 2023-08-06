from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ImportPy:
	"""ImportPy commands group definition. 50 total commands, 2 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("importPy", core, parent)

	@property
	def pdw(self):
		"""pdw commands group. 4 Sub-classes, 2 commands."""
		if not hasattr(self, '_pdw'):
			from .Pdw import Pdw
			self._pdw = Pdw(self._core, self._cmd_group)
		return self._pdw

	@property
	def view(self):
		"""view commands group. 2 Sub-classes, 1 commands."""
		if not hasattr(self, '_view'):
			from .View import View
			self._view = View(self._core, self._cmd_group)
		return self._view

	def clone(self) -> 'ImportPy':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ImportPy(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
