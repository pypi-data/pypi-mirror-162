from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class File:
	"""File commands group definition. 6 total commands, 2 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("file", core, parent)

	@property
	def pdw(self):
		"""pdw commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_pdw'):
			from .Pdw import Pdw
			self._pdw = Pdw(self._core, self._cmd_group)
		return self._pdw

	@property
	def template(self):
		"""template commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_template'):
			from .Template import Template
			self._template = Template(self._core, self._cmd_group)
		return self._template

	def clone(self) -> 'File':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = File(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
