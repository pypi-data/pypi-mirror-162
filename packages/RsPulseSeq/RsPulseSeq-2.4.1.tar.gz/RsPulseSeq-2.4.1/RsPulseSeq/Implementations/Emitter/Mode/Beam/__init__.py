from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Beam:
	"""Beam commands group definition. 11 total commands, 2 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("beam", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	@property
	def offset(self):
		"""offset commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_offset'):
			from .Offset import Offset
			self._offset = Offset(self._core, self._cmd_group)
		return self._offset

	def clear(self) -> None:
		"""SCPI: EMITter:MODE:BEAM:CLEar \n
		Snippet: driver.emitter.mode.beam.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'EMITter:MODE:BEAM:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: EMITter:MODE:BEAM:CLEar \n
		Snippet: driver.emitter.mode.beam.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'EMITter:MODE:BEAM:CLEar', opc_timeout_ms)

	def get_count(self) -> float:
		"""SCPI: EMITter:MODE:BEAM:COUNt \n
		Snippet: value: float = driver.emitter.mode.beam.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('EMITter:MODE:BEAM:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: EMITter:MODE:BEAM:DELete \n
		Snippet: driver.emitter.mode.beam.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'EMITter:MODE:BEAM:DELete {param}')

	def get_name(self) -> str:
		"""SCPI: EMITter:MODE:BEAM:NAME \n
		Snippet: value: str = driver.emitter.mode.beam.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('EMITter:MODE:BEAM:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: EMITter:MODE:BEAM:NAME \n
		Snippet: driver.emitter.mode.beam.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'EMITter:MODE:BEAM:NAME {param}')

	def get_select(self) -> float:
		"""SCPI: EMITter:MODE:BEAM:SELect \n
		Snippet: value: float = driver.emitter.mode.beam.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('EMITter:MODE:BEAM:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: EMITter:MODE:BEAM:SELect \n
		Snippet: driver.emitter.mode.beam.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'EMITter:MODE:BEAM:SELect {param}')

	def get_sequence(self) -> str:
		"""SCPI: EMITter:MODE:BEAM:SEQuence \n
		Snippet: value: str = driver.emitter.mode.beam.get_sequence() \n
		Assigns a pulse sequence, see method RsPulseSeq.Sequence.create. \n
			:return: sequence: string
		"""
		response = self._core.io.query_str('EMITter:MODE:BEAM:SEQuence?')
		return trim_str_response(response)

	def set_sequence(self, sequence: str) -> None:
		"""SCPI: EMITter:MODE:BEAM:SEQuence \n
		Snippet: driver.emitter.mode.beam.set_sequence(sequence = '1') \n
		Assigns a pulse sequence, see method RsPulseSeq.Sequence.create. \n
			:param sequence: string
		"""
		param = Conversions.value_to_quoted_str(sequence)
		self._core.io.write(f'EMITter:MODE:BEAM:SEQuence {param}')

	def get_state(self) -> bool:
		"""SCPI: EMITter:MODE:BEAM:STATe \n
		Snippet: value: bool = driver.emitter.mode.beam.get_state() \n
		Activates a beam. \n
			:return: state: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('EMITter:MODE:BEAM:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, state: bool) -> None:
		"""SCPI: EMITter:MODE:BEAM:STATe \n
		Snippet: driver.emitter.mode.beam.set_state(state = False) \n
		Activates a beam. \n
			:param state: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'EMITter:MODE:BEAM:STATe {param}')

	def clone(self) -> 'Beam':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Beam(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
