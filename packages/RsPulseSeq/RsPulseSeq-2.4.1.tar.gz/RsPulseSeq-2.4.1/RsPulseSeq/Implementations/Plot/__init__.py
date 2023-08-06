from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Plot:
	"""Plot commands group definition. 3 total commands, 1 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("plot", core, parent)

	@property
	def polar(self):
		"""polar commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_polar'):
			from .Polar import Polar
			self._polar = Polar(self._core, self._cmd_group)
		return self._polar

	def clone(self) -> 'Plot':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Plot(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
