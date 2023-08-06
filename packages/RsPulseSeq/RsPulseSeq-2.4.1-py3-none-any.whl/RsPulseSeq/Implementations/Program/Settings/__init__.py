from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Settings:
	"""Settings commands group definition. 2 total commands, 2 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("settings", core, parent)

	@property
	def accept(self):
		"""accept commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_accept'):
			from .Accept import Accept
			self._accept = Accept(self._core, self._cmd_group)
		return self._accept

	@property
	def reject(self):
		"""reject commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_reject'):
			from .Reject import Reject
			self._reject = Reject(self._core, self._cmd_group)
		return self._reject

	def clone(self) -> 'Settings':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Settings(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
