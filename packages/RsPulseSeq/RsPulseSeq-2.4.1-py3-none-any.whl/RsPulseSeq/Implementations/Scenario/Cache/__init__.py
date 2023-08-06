from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Cache:
	"""Cache commands group definition. 8 total commands, 2 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cache", core, parent)

	@property
	def repository(self):
		"""repository commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_repository'):
			from .Repository import Repository
			self._repository = Repository(self._core, self._cmd_group)
		return self._repository

	@property
	def volatile(self):
		"""volatile commands group. 2 Sub-classes, 2 commands."""
		if not hasattr(self, '_volatile'):
			from .Volatile import Volatile
			self._volatile = Volatile(self._core, self._cmd_group)
		return self._volatile

	def clone(self) -> 'Cache':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Cache(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
