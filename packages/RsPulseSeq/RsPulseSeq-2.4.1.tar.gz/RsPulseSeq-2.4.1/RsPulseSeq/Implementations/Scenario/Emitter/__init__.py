from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Emitter:
	"""Emitter commands group definition. 7 total commands, 2 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("emitter", core, parent)

	@property
	def direction(self):
		"""direction commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_direction'):
			from .Direction import Direction
			self._direction = Direction(self._core, self._cmd_group)
		return self._direction

	@property
	def mode(self):
		"""mode commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_mode'):
			from .Mode import Mode
			self._mode = Mode(self._core, self._cmd_group)
		return self._mode

	def clear(self) -> None:
		"""SCPI: SCENario:EMITter:CLEar \n
		Snippet: driver.scenario.emitter.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'SCENario:EMITter:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:EMITter:CLEar \n
		Snippet: driver.scenario.emitter.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:EMITter:CLEar', opc_timeout_ms)

	def get_value(self) -> str:
		"""SCPI: SCENario:EMITter \n
		Snippet: value: str = driver.scenario.emitter.get_value() \n
		Assigns an existing emitter or an existing waveform, see method RsPulseSeq.Waveform.catalog and method RsPulseSeq.Emitter.
		catalog. \n
			:return: emitter: string
		"""
		response = self._core.io.query_str('SCENario:EMITter?')
		return trim_str_response(response)

	def set_value(self, emitter: str) -> None:
		"""SCPI: SCENario:EMITter \n
		Snippet: driver.scenario.emitter.set_value(emitter = '1') \n
		Assigns an existing emitter or an existing waveform, see method RsPulseSeq.Waveform.catalog and method RsPulseSeq.Emitter.
		catalog. \n
			:param emitter: string
		"""
		param = Conversions.value_to_quoted_str(emitter)
		self._core.io.write(f'SCENario:EMITter {param}')

	def clone(self) -> 'Emitter':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Emitter(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
