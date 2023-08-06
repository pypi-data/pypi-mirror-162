from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BlankRanges:
	"""BlankRanges commands group definition. 7 total commands, 1 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("blankRanges", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	def clear(self) -> None:
		"""SCPI: PLATform:EMITter:BLANkranges:CLEar \n
		Snippet: driver.platform.emitter.blankRanges.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'PLATform:EMITter:BLANkranges:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: PLATform:EMITter:BLANkranges:CLEar \n
		Snippet: driver.platform.emitter.blankRanges.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PLATform:EMITter:BLANkranges:CLEar', opc_timeout_ms)

	def get_count(self) -> float:
		"""SCPI: PLATform:EMITter:BLANkranges:COUNt \n
		Snippet: value: float = driver.platform.emitter.blankRanges.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('PLATform:EMITter:BLANkranges:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: PLATform:EMITter:BLANkranges:DELete \n
		Snippet: driver.platform.emitter.blankRanges.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'PLATform:EMITter:BLANkranges:DELete {param}')

	def get_select(self) -> float:
		"""SCPI: PLATform:EMITter:BLANkranges:SELect \n
		Snippet: value: float = driver.platform.emitter.blankRanges.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('PLATform:EMITter:BLANkranges:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: PLATform:EMITter:BLANkranges:SELect \n
		Snippet: driver.platform.emitter.blankRanges.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'PLATform:EMITter:BLANkranges:SELect {param}')

	def get_start(self) -> float:
		"""SCPI: PLATform:EMITter:BLANkranges:STARt \n
		Snippet: value: float = driver.platform.emitter.blankRanges.get_start() \n
		Sets the start angle for the selected blank range. The reference value (i.e. 0°) is the configured 'Azimuth' value for
		the selected emitter. Use together with method RsPulseSeq.Platform.Emitter.BlankRanges.select. To configure several blank
		ranges with a single command, you can use PLATform:EMITter:BLANkranges . This approach is more efficient than using
		several blank range start/stop commands. \n
			:return: start: float Range: 0 to 360
		"""
		response = self._core.io.query_str('PLATform:EMITter:BLANkranges:STARt?')
		return Conversions.str_to_float(response)

	def set_start(self, start: float) -> None:
		"""SCPI: PLATform:EMITter:BLANkranges:STARt \n
		Snippet: driver.platform.emitter.blankRanges.set_start(start = 1.0) \n
		Sets the start angle for the selected blank range. The reference value (i.e. 0°) is the configured 'Azimuth' value for
		the selected emitter. Use together with method RsPulseSeq.Platform.Emitter.BlankRanges.select. To configure several blank
		ranges with a single command, you can use PLATform:EMITter:BLANkranges . This approach is more efficient than using
		several blank range start/stop commands. \n
			:param start: float Range: 0 to 360
		"""
		param = Conversions.decimal_value_to_str(start)
		self._core.io.write(f'PLATform:EMITter:BLANkranges:STARt {param}')

	def get_stop(self) -> float:
		"""SCPI: PLATform:EMITter:BLANkranges:STOP \n
		Snippet: value: float = driver.platform.emitter.blankRanges.get_stop() \n
		Sets the stop angle for the selected 'Blank Range'. The reference value (i.e. 0°) is the configured 'Azimuth' value for
		the selected emitter. Use together with method RsPulseSeq.Platform.Emitter.BlankRanges.select. To configure several blank
		ranges with a single command, you can use PLATform:EMITter:BLANkranges . This approach is more efficient than using
		several blank range start/stop commands. \n
			:return: stop: float Range: 0 to 360
		"""
		response = self._core.io.query_str('PLATform:EMITter:BLANkranges:STOP?')
		return Conversions.str_to_float(response)

	def set_stop(self, stop: float) -> None:
		"""SCPI: PLATform:EMITter:BLANkranges:STOP \n
		Snippet: driver.platform.emitter.blankRanges.set_stop(stop = 1.0) \n
		Sets the stop angle for the selected 'Blank Range'. The reference value (i.e. 0°) is the configured 'Azimuth' value for
		the selected emitter. Use together with method RsPulseSeq.Platform.Emitter.BlankRanges.select. To configure several blank
		ranges with a single command, you can use PLATform:EMITter:BLANkranges . This approach is more efficient than using
		several blank range start/stop commands. \n
			:param stop: float Range: 0 to 360
		"""
		param = Conversions.decimal_value_to_str(stop)
		self._core.io.write(f'PLATform:EMITter:BLANkranges:STOP {param}')

	def clone(self) -> 'BlankRanges':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = BlankRanges(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
