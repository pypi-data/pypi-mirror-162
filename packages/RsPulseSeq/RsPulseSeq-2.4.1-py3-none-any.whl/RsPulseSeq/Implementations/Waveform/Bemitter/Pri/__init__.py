from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Pri:
	"""Pri commands group definition. 2 total commands, 1 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pri", core, parent)

	@property
	def ratio(self):
		"""ratio commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_ratio'):
			from .Ratio import Ratio
			self._ratio = Ratio(self._core, self._cmd_group)
		return self._ratio

	def clone(self) -> 'Pri':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Pri(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
