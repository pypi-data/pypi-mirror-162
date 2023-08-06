from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Antenna:
	"""Antenna commands group definition. 17 total commands, 3 Subgroups, 8 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("antenna", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	@property
	def direction(self):
		"""direction commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_direction'):
			from .Direction import Direction
			self._direction = Direction(self._core, self._cmd_group)
		return self._direction

	@property
	def position(self):
		"""position commands group. 0 Sub-classes, 5 commands."""
		if not hasattr(self, '_position'):
			from .Position import Position
			self._position = Position(self._core, self._cmd_group)
		return self._position

	def get_alias(self) -> str:
		"""SCPI: RECeiver:ANTenna:ALIas \n
		Snippet: value: str = driver.receiver.antenna.get_alias() \n
		Sets an alias name for the selected antenna element. \n
			:return: alias: string
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:ALIas?')
		return trim_str_response(response)

	def set_alias(self, alias: str) -> None:
		"""SCPI: RECeiver:ANTenna:ALIas \n
		Snippet: driver.receiver.antenna.set_alias(alias = '1') \n
		Sets an alias name for the selected antenna element. \n
			:param alias: string
		"""
		param = Conversions.value_to_quoted_str(alias)
		self._core.io.write(f'RECeiver:ANTenna:ALIas {param}')

	def get_bm(self) -> str:
		"""SCPI: RECeiver:ANTenna:BM \n
		Snippet: value: str = driver.receiver.antenna.get_bm() \n
		No command help available \n
			:return: bm: No help available
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:BM?')
		return trim_str_response(response)

	def set_bm(self, bm: str) -> None:
		"""SCPI: RECeiver:ANTenna:BM \n
		Snippet: driver.receiver.antenna.set_bm(bm = '1') \n
		No command help available \n
			:param bm: No help available
		"""
		param = Conversions.value_to_quoted_str(bm)
		self._core.io.write(f'RECeiver:ANTenna:BM {param}')

	def clear(self) -> None:
		"""SCPI: RECeiver:ANTenna:CLEar \n
		Snippet: driver.receiver.antenna.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'RECeiver:ANTenna:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: RECeiver:ANTenna:CLEar \n
		Snippet: driver.receiver.antenna.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'RECeiver:ANTenna:CLEar', opc_timeout_ms)

	def delete(self) -> None:
		"""SCPI: RECeiver:ANTenna:DELete \n
		Snippet: driver.receiver.antenna.delete() \n
		Deletes the particular item. \n
		"""
		self._core.io.write(f'RECeiver:ANTenna:DELete')

	def delete_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: RECeiver:ANTenna:DELete \n
		Snippet: driver.receiver.antenna.delete_with_opc() \n
		Deletes the particular item. \n
		Same as delete, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'RECeiver:ANTenna:DELete', opc_timeout_ms)

	def get_gain(self) -> float:
		"""SCPI: RECeiver:ANTenna:GAIN \n
		Snippet: value: float = driver.receiver.antenna.get_gain() \n
		Sets the gain of the individual antenna element. \n
			:return: gain: float Range: -120 to 120
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:GAIN?')
		return Conversions.str_to_float(response)

	def set_gain(self, gain: float) -> None:
		"""SCPI: RECeiver:ANTenna:GAIN \n
		Snippet: driver.receiver.antenna.set_gain(gain = 1.0) \n
		Sets the gain of the individual antenna element. \n
			:param gain: float Range: -120 to 120
		"""
		param = Conversions.decimal_value_to_str(gain)
		self._core.io.write(f'RECeiver:ANTenna:GAIN {param}')

	def get_pattern(self) -> str:
		"""SCPI: RECeiver:ANTenna:PATTern \n
		Snippet: value: str = driver.receiver.antenna.get_pattern() \n
		Assigns an existing antenna pattern, see method RsPulseSeq.Antenna.catalog. \n
			:return: pattern: string
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:PATTern?')
		return trim_str_response(response)

	def set_pattern(self, pattern: str) -> None:
		"""SCPI: RECeiver:ANTenna:PATTern \n
		Snippet: driver.receiver.antenna.set_pattern(pattern = '1') \n
		Assigns an existing antenna pattern, see method RsPulseSeq.Antenna.catalog. \n
			:param pattern: string
		"""
		param = Conversions.value_to_quoted_str(pattern)
		self._core.io.write(f'RECeiver:ANTenna:PATTern {param}')

	def get_scan(self) -> str:
		"""SCPI: RECeiver:ANTenna:SCAN \n
		Snippet: value: str = driver.receiver.antenna.get_scan() \n
		Sets the antenna scan. \n
			:return: scan: string
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:SCAN?')
		return trim_str_response(response)

	def set_scan(self, scan: str) -> None:
		"""SCPI: RECeiver:ANTenna:SCAN \n
		Snippet: driver.receiver.antenna.set_scan(scan = '1') \n
		Sets the antenna scan. \n
			:param scan: string
		"""
		param = Conversions.value_to_quoted_str(scan)
		self._core.io.write(f'RECeiver:ANTenna:SCAN {param}')

	def get_select(self) -> float:
		"""SCPI: RECeiver:ANTenna:SELect \n
		Snippet: value: float = driver.receiver.antenna.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: RECeiver:ANTenna:SELect \n
		Snippet: driver.receiver.antenna.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'RECeiver:ANTenna:SELect {param}')

	def clone(self) -> 'Antenna':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Antenna(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
