from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Entry:
	"""Entry commands group definition. 11 total commands, 1 Subgroups, 10 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("entry", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	def get_azimuth(self) -> float:
		"""SCPI: SCAN:CUSTom:ENTRy:AZIMuth \n
		Snippet: value: float = driver.scan.custom.entry.get_azimuth() \n
		Sets the azimuth of the scan position. \n
			:return: azimuth: float Range: -180 to 180
		"""
		response = self._core.io.query_str('SCAN:CUSTom:ENTRy:AZIMuth?')
		return Conversions.str_to_float(response)

	def set_azimuth(self, azimuth: float) -> None:
		"""SCPI: SCAN:CUSTom:ENTRy:AZIMuth \n
		Snippet: driver.scan.custom.entry.set_azimuth(azimuth = 1.0) \n
		Sets the azimuth of the scan position. \n
			:param azimuth: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(azimuth)
		self._core.io.write(f'SCAN:CUSTom:ENTRy:AZIMuth {param}')

	def clear(self) -> None:
		"""SCPI: SCAN:CUSTom:ENTRy:CLEar \n
		Snippet: driver.scan.custom.entry.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'SCAN:CUSTom:ENTRy:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCAN:CUSTom:ENTRy:CLEar \n
		Snippet: driver.scan.custom.entry.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCAN:CUSTom:ENTRy:CLEar', opc_timeout_ms)

	def get_count(self) -> float:
		"""SCPI: SCAN:CUSTom:ENTRy:COUNt \n
		Snippet: value: float = driver.scan.custom.entry.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('SCAN:CUSTom:ENTRy:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: SCAN:CUSTom:ENTRy:DELete \n
		Snippet: driver.scan.custom.entry.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'SCAN:CUSTom:ENTRy:DELete {param}')

	def get_dwell(self) -> float:
		"""SCPI: SCAN:CUSTom:ENTRy:DWELl \n
		Snippet: value: float = driver.scan.custom.entry.get_dwell() \n
		Sets how long the scan stays in a position. \n
			:return: dwell: float Range: 0 to 3600
		"""
		response = self._core.io.query_str('SCAN:CUSTom:ENTRy:DWELl?')
		return Conversions.str_to_float(response)

	def set_dwell(self, dwell: float) -> None:
		"""SCPI: SCAN:CUSTom:ENTRy:DWELl \n
		Snippet: driver.scan.custom.entry.set_dwell(dwell = 1.0) \n
		Sets how long the scan stays in a position. \n
			:param dwell: float Range: 0 to 3600
		"""
		param = Conversions.decimal_value_to_str(dwell)
		self._core.io.write(f'SCAN:CUSTom:ENTRy:DWELl {param}')

	def get_elevation(self) -> float:
		"""SCPI: SCAN:CUSTom:ENTRy:ELEVation \n
		Snippet: value: float = driver.scan.custom.entry.get_elevation() \n
		Sets the elevation of the scan position. \n
			:return: elevation: float Range: -90 to 90
		"""
		response = self._core.io.query_str('SCAN:CUSTom:ENTRy:ELEVation?')
		return Conversions.str_to_float(response)

	def set_elevation(self, elevation: float) -> None:
		"""SCPI: SCAN:CUSTom:ENTRy:ELEVation \n
		Snippet: driver.scan.custom.entry.set_elevation(elevation = 1.0) \n
		Sets the elevation of the scan position. \n
			:param elevation: float Range: -90 to 90
		"""
		param = Conversions.decimal_value_to_str(elevation)
		self._core.io.write(f'SCAN:CUSTom:ENTRy:ELEVation {param}')

	def set_insert(self, insert: float) -> None:
		"""SCPI: SCAN:CUSTom:ENTRy:INSert \n
		Snippet: driver.scan.custom.entry.set_insert(insert = 1.0) \n
		Inserts a new item before the selected one. \n
			:param insert: float
		"""
		param = Conversions.decimal_value_to_str(insert)
		self._core.io.write(f'SCAN:CUSTom:ENTRy:INSert {param}')

	def get_jump_type(self) -> bool:
		"""SCPI: SCAN:CUSTom:ENTRy:JUMPtype \n
		Snippet: value: bool = driver.scan.custom.entry.get_jump_type() \n
		Defines how to move to the next position, either with a jump or with a transition. For transitions, you need to define a
		transition time. \n
			:return: jump_type: ON| OFF| 1| 0 ON | 1 Jump enabled. OFF | 0 Transition enabled.
		"""
		response = self._core.io.query_str('SCAN:CUSTom:ENTRy:JUMPtype?')
		return Conversions.str_to_bool(response)

	def set_jump_type(self, jump_type: bool) -> None:
		"""SCPI: SCAN:CUSTom:ENTRy:JUMPtype \n
		Snippet: driver.scan.custom.entry.set_jump_type(jump_type = False) \n
		Defines how to move to the next position, either with a jump or with a transition. For transitions, you need to define a
		transition time. \n
			:param jump_type: ON| OFF| 1| 0 ON | 1 Jump enabled. OFF | 0 Transition enabled.
		"""
		param = Conversions.bool_to_str(jump_type)
		self._core.io.write(f'SCAN:CUSTom:ENTRy:JUMPtype {param}')

	def get_select(self) -> float:
		"""SCPI: SCAN:CUSTom:ENTRy:SELect \n
		Snippet: value: float = driver.scan.custom.entry.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('SCAN:CUSTom:ENTRy:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: SCAN:CUSTom:ENTRy:SELect \n
		Snippet: driver.scan.custom.entry.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'SCAN:CUSTom:ENTRy:SELect {param}')

	def get_trans_time(self) -> float:
		"""SCPI: SCAN:CUSTom:ENTRy:TRANstime \n
		Snippet: value: float = driver.scan.custom.entry.get_trans_time() \n
		Sets the time for the transition between two positions. \n
			:return: trans_time: float Range: 0 to 3600
		"""
		response = self._core.io.query_str('SCAN:CUSTom:ENTRy:TRANstime?')
		return Conversions.str_to_float(response)

	def set_trans_time(self, trans_time: float) -> None:
		"""SCPI: SCAN:CUSTom:ENTRy:TRANstime \n
		Snippet: driver.scan.custom.entry.set_trans_time(trans_time = 1.0) \n
		Sets the time for the transition between two positions. \n
			:param trans_time: float Range: 0 to 3600
		"""
		param = Conversions.decimal_value_to_str(trans_time)
		self._core.io.write(f'SCAN:CUSTom:ENTRy:TRANstime {param}')

	def clone(self) -> 'Entry':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Entry(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
