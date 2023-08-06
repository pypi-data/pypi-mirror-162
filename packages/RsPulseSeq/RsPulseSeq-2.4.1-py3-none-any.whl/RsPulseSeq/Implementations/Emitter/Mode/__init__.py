from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Mode:
	"""Mode commands group definition. 22 total commands, 4 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	@property
	def antenna(self):
		"""antenna commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_antenna'):
			from .Antenna import Antenna
			self._antenna = Antenna(self._core, self._cmd_group)
		return self._antenna

	@property
	def beam(self):
		"""beam commands group. 2 Sub-classes, 7 commands."""
		if not hasattr(self, '_beam'):
			from .Beam import Beam
			self._beam = Beam(self._core, self._cmd_group)
		return self._beam

	@property
	def scan(self):
		"""scan commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_scan'):
			from .Scan import Scan
			self._scan = Scan(self._core, self._cmd_group)
		return self._scan

	def get_id(self) -> float:
		"""SCPI: EMITter:MODE:ID \n
		Snippet: value: float = driver.emitter.mode.get_id() \n
		No command help available \n
			:return: idn: float Range: 1 to 65536
		"""
		response = self._core.io.query_str('EMITter:MODE:ID?')
		return Conversions.str_to_float(response)

	def set_id(self, idn: float) -> None:
		"""SCPI: EMITter:MODE:ID \n
		Snippet: driver.emitter.mode.set_id(idn = 1.0) \n
		No command help available \n
			:param idn: float Range: 1 to 65536
		"""
		param = Conversions.decimal_value_to_str(idn)
		self._core.io.write(f'EMITter:MODE:ID {param}')

	def clear(self) -> None:
		"""SCPI: EMITter:MODE:CLEar \n
		Snippet: driver.emitter.mode.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'EMITter:MODE:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: EMITter:MODE:CLEar \n
		Snippet: driver.emitter.mode.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'EMITter:MODE:CLEar', opc_timeout_ms)

	def get_count(self) -> float:
		"""SCPI: EMITter:MODE:COUNt \n
		Snippet: value: float = driver.emitter.mode.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('EMITter:MODE:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: EMITter:MODE:DELete \n
		Snippet: driver.emitter.mode.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'EMITter:MODE:DELete {param}')

	def get_name(self) -> str:
		"""SCPI: EMITter:MODE:NAME \n
		Snippet: value: str = driver.emitter.mode.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('EMITter:MODE:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: EMITter:MODE:NAME \n
		Snippet: driver.emitter.mode.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'EMITter:MODE:NAME {param}')

	def get_select(self) -> float:
		"""SCPI: EMITter:MODE:SELect \n
		Snippet: value: float = driver.emitter.mode.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('EMITter:MODE:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: EMITter:MODE:SELect \n
		Snippet: driver.emitter.mode.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'EMITter:MODE:SELect {param}')

	def clone(self) -> 'Mode':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Mode(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
