from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Move:
	"""Move commands group definition. 4 total commands, 3 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("move", core, parent)

	@property
	def backwards(self):
		"""backwards commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_backwards'):
			from .Backwards import Backwards
			self._backwards = Backwards(self._core, self._cmd_group)
		return self._backwards

	@property
	def end(self):
		"""end commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_end'):
			from .End import End
			self._end = End(self._core, self._cmd_group)
		return self._end

	@property
	def forward(self):
		"""forward commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_forward'):
			from .Forward import Forward
			self._forward = Forward(self._core, self._cmd_group)
		return self._forward

	def start(self) -> None:
		"""SCPI: IMPort:VIEW:MOVE:STARt \n
		Snippet: driver.importPy.view.move.start() \n
		Goes to the first/next/previous/last page. \n
		"""
		self._core.io.write(f'IMPort:VIEW:MOVE:STARt')

	def start_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: IMPort:VIEW:MOVE:STARt \n
		Snippet: driver.importPy.view.move.start_with_opc() \n
		Goes to the first/next/previous/last page. \n
		Same as start, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'IMPort:VIEW:MOVE:STARt', opc_timeout_ms)

	def clone(self) -> 'Move':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Move(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
