from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Data:
	"""Data commands group definition. 11 total commands, 1 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("data", core, parent)

	@property
	def item(self):
		"""item commands group. 1 Sub-classes, 4 commands."""
		if not hasattr(self, '_item'):
			from .Item import Item
			self._item = Item(self._core, self._cmd_group)
		return self._item

	def clear(self) -> None:
		"""SCPI: PULSe:ENVelope:DATA:CLEar \n
		Snippet: driver.pulse.envelope.data.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'PULSe:ENVelope:DATA:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: PULSe:ENVelope:DATA:CLEar \n
		Snippet: driver.pulse.envelope.data.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PULSe:ENVelope:DATA:CLEar', opc_timeout_ms)

	def get_load(self) -> str:
		"""SCPI: PULSe:ENVelope:DATA:LOAD \n
		Snippet: value: str = driver.pulse.envelope.data.get_load() \n
		Loads an envelope description form an ASCII file. \n
			:return: load: string File path, file name, and file extension
		"""
		response = self._core.io.query_str('PULSe:ENVelope:DATA:LOAD?')
		return trim_str_response(response)

	def set_load(self, load: str) -> None:
		"""SCPI: PULSe:ENVelope:DATA:LOAD \n
		Snippet: driver.pulse.envelope.data.set_load(load = '1') \n
		Loads an envelope description form an ASCII file. \n
			:param load: string File path, file name, and file extension
		"""
		param = Conversions.value_to_quoted_str(load)
		self._core.io.write(f'PULSe:ENVelope:DATA:LOAD {param}')

	def get_multiplier(self) -> float:
		"""SCPI: PULSe:ENVelope:DATA:MULTiplier \n
		Snippet: value: float = driver.pulse.envelope.data.get_multiplier() \n
		Sets a multiplier factor. \n
			:return: multiplier: float Range: -100 to 100
		"""
		response = self._core.io.query_str('PULSe:ENVelope:DATA:MULTiplier?')
		return Conversions.str_to_float(response)

	def set_multiplier(self, multiplier: float) -> None:
		"""SCPI: PULSe:ENVelope:DATA:MULTiplier \n
		Snippet: driver.pulse.envelope.data.set_multiplier(multiplier = 1.0) \n
		Sets a multiplier factor. \n
			:param multiplier: float Range: -100 to 100
		"""
		param = Conversions.decimal_value_to_str(multiplier)
		self._core.io.write(f'PULSe:ENVelope:DATA:MULTiplier {param}')

	def get_offset(self) -> float:
		"""SCPI: PULSe:ENVelope:DATA:OFFSet \n
		Snippet: value: float = driver.pulse.envelope.data.get_offset() \n
		Sets an offset for the envelope. \n
			:return: offset: float Range: -100 to 100
		"""
		response = self._core.io.query_str('PULSe:ENVelope:DATA:OFFSet?')
		return Conversions.str_to_float(response)

	def set_offset(self, offset: float) -> None:
		"""SCPI: PULSe:ENVelope:DATA:OFFSet \n
		Snippet: driver.pulse.envelope.data.set_offset(offset = 1.0) \n
		Sets an offset for the envelope. \n
			:param offset: float Range: -100 to 100
		"""
		param = Conversions.decimal_value_to_str(offset)
		self._core.io.write(f'PULSe:ENVelope:DATA:OFFSet {param}')

	def get_save(self) -> str:
		"""SCPI: PULSe:ENVelope:DATA:SAVE \n
		Snippet: value: str = driver.pulse.envelope.data.get_save() \n
		Stores the custom envelope into file. \n
			:return: save: string File path, file name, and file extension
		"""
		response = self._core.io.query_str('PULSe:ENVelope:DATA:SAVE?')
		return trim_str_response(response)

	def set_save(self, save: str) -> None:
		"""SCPI: PULSe:ENVelope:DATA:SAVE \n
		Snippet: driver.pulse.envelope.data.set_save(save = '1') \n
		Stores the custom envelope into file. \n
			:param save: string File path, file name, and file extension
		"""
		param = Conversions.value_to_quoted_str(save)
		self._core.io.write(f'PULSe:ENVelope:DATA:SAVE {param}')

	# noinspection PyTypeChecker
	def get_unit(self) -> enums.DataUnit:
		"""SCPI: PULSe:ENVelope:DATA:UNIT \n
		Snippet: value: enums.DataUnit = driver.pulse.envelope.data.get_unit() \n
		Sets the data format. \n
			:return: unit: VOLTage| WATTs| DB
		"""
		response = self._core.io.query_str('PULSe:ENVelope:DATA:UNIT?')
		return Conversions.str_to_scalar_enum(response, enums.DataUnit)

	def set_unit(self, unit: enums.DataUnit) -> None:
		"""SCPI: PULSe:ENVelope:DATA:UNIT \n
		Snippet: driver.pulse.envelope.data.set_unit(unit = enums.DataUnit.DB) \n
		Sets the data format. \n
			:param unit: VOLTage| WATTs| DB
		"""
		param = Conversions.enum_scalar_to_str(unit, enums.DataUnit)
		self._core.io.write(f'PULSe:ENVelope:DATA:UNIT {param}')

	def clone(self) -> 'Data':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Data(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
