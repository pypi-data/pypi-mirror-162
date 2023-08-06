from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Csequence:
	"""Csequence commands group definition. 8 total commands, 1 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("csequence", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	def get_alias(self) -> str:
		"""SCPI: SCENario:CSEQuence:ALIas \n
		Snippet: value: str = driver.scenario.csequence.get_alias() \n
		Enters an alias name. \n
			:return: alias: string
		"""
		response = self._core.io.query_str('SCENario:CSEQuence:ALIas?')
		return trim_str_response(response)

	def set_alias(self, alias: str) -> None:
		"""SCPI: SCENario:CSEQuence:ALIas \n
		Snippet: driver.scenario.csequence.set_alias(alias = '1') \n
		Enters an alias name. \n
			:param alias: string
		"""
		param = Conversions.value_to_quoted_str(alias)
		self._core.io.write(f'SCENario:CSEQuence:ALIas {param}')

	def clear(self) -> None:
		"""SCPI: SCENario:CSEQuence:CLEar \n
		Snippet: driver.scenario.csequence.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'SCENario:CSEQuence:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:CSEQuence:CLEar \n
		Snippet: driver.scenario.csequence.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:CSEQuence:CLEar', opc_timeout_ms)

	def get_current(self) -> float:
		"""SCPI: SCENario:CSEQuence:CURRent \n
		Snippet: value: float = driver.scenario.csequence.get_current() \n
		Sets the sequence/emitter that is used by the scenario. \n
			:return: current: float Number of the sequence/emitter in the list with multiple sequences
		"""
		response = self._core.io.query_str('SCENario:CSEQuence:CURRent?')
		return Conversions.str_to_float(response)

	def set_current(self, current: float) -> None:
		"""SCPI: SCENario:CSEQuence:CURRent \n
		Snippet: driver.scenario.csequence.set_current(current = 1.0) \n
		Sets the sequence/emitter that is used by the scenario. \n
			:param current: float Number of the sequence/emitter in the list with multiple sequences
		"""
		param = Conversions.decimal_value_to_str(current)
		self._core.io.write(f'SCENario:CSEQuence:CURRent {param}')

	def delete(self, delete: float) -> None:
		"""SCPI: SCENario:CSEQuence:DELete \n
		Snippet: driver.scenario.csequence.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'SCENario:CSEQuence:DELete {param}')

	def get_select(self) -> float:
		"""SCPI: SCENario:CSEQuence:SELect \n
		Snippet: value: float = driver.scenario.csequence.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('SCENario:CSEQuence:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: SCENario:CSEQuence:SELect \n
		Snippet: driver.scenario.csequence.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'SCENario:CSEQuence:SELect {param}')

	def get_variable(self) -> str:
		"""SCPI: SCENario:CSEQuence:VARiable \n
		Snippet: value: str = driver.scenario.csequence.get_variable() \n
		Sets the collection variable. \n
			:return: variable: string
		"""
		response = self._core.io.query_str('SCENario:CSEQuence:VARiable?')
		return trim_str_response(response)

	def set_variable(self, variable: str) -> None:
		"""SCPI: SCENario:CSEQuence:VARiable \n
		Snippet: driver.scenario.csequence.set_variable(variable = '1') \n
		Sets the collection variable. \n
			:param variable: string
		"""
		param = Conversions.value_to_quoted_str(variable)
		self._core.io.write(f'SCENario:CSEQuence:VARiable {param}')

	def get_value(self) -> str:
		"""SCPI: SCENario:CSEQuence \n
		Snippet: value: str = driver.scenario.csequence.get_value() \n
		Select an existing sequence, see method RsPulseSeq.Sequence.catalog. \n
			:return: csequence: string
		"""
		response = self._core.io.query_str('SCENario:CSEQuence?')
		return trim_str_response(response)

	def set_value(self, csequence: str) -> None:
		"""SCPI: SCENario:CSEQuence \n
		Snippet: driver.scenario.csequence.set_value(csequence = '1') \n
		Select an existing sequence, see method RsPulseSeq.Sequence.catalog. \n
			:param csequence: string
		"""
		param = Conversions.value_to_quoted_str(csequence)
		self._core.io.write(f'SCENario:CSEQuence {param}')

	def clone(self) -> 'Csequence':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Csequence(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
