from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Pchirp:
	"""Pchirp commands group definition. 8 total commands, 1 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pchirp", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	def clear(self) -> None:
		"""SCPI: PULSe:MOP:PCHirp:CLEar \n
		Snippet: driver.pulse.mop.pchirp.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'PULSe:MOP:PCHirp:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: PULSe:MOP:PCHirp:CLEar \n
		Snippet: driver.pulse.mop.pchirp.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PULSe:MOP:PCHirp:CLEar', opc_timeout_ms)

	def get_coefficient(self) -> float:
		"""SCPI: PULSe:MOP:PCHirp:COEFficient \n
		Snippet: value: float = driver.pulse.mop.pchirp.get_coefficient() \n
		Sets the coefficient of the chirp polynomial. \n
			:return: coefficient: float Range: -1e+32 to 1e+32
		"""
		response = self._core.io.query_str('PULSe:MOP:PCHirp:COEFficient?')
		return Conversions.str_to_float(response)

	def set_coefficient(self, coefficient: float) -> None:
		"""SCPI: PULSe:MOP:PCHirp:COEFficient \n
		Snippet: driver.pulse.mop.pchirp.set_coefficient(coefficient = 1.0) \n
		Sets the coefficient of the chirp polynomial. \n
			:param coefficient: float Range: -1e+32 to 1e+32
		"""
		param = Conversions.decimal_value_to_str(coefficient)
		self._core.io.write(f'PULSe:MOP:PCHirp:COEFficient {param}')

	def get_count(self) -> float:
		"""SCPI: PULSe:MOP:PCHirp:COUNt \n
		Snippet: value: float = driver.pulse.mop.pchirp.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('PULSe:MOP:PCHirp:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: PULSe:MOP:PCHirp:DELete \n
		Snippet: driver.pulse.mop.pchirp.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'PULSe:MOP:PCHirp:DELete {param}')

	def set_insert(self, insert: float) -> None:
		"""SCPI: PULSe:MOP:PCHirp:INSert \n
		Snippet: driver.pulse.mop.pchirp.set_insert(insert = 1.0) \n
		Inserts a new item before the selected one. \n
			:param insert: float
		"""
		param = Conversions.decimal_value_to_str(insert)
		self._core.io.write(f'PULSe:MOP:PCHirp:INSert {param}')

	def get_select(self) -> float:
		"""SCPI: PULSe:MOP:PCHirp:SELect \n
		Snippet: value: float = driver.pulse.mop.pchirp.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('PULSe:MOP:PCHirp:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: PULSe:MOP:PCHirp:SELect \n
		Snippet: driver.pulse.mop.pchirp.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'PULSe:MOP:PCHirp:SELect {param}')

	def get_term(self) -> float:
		"""SCPI: PULSe:MOP:PCHirp:TERM \n
		Snippet: value: float = driver.pulse.mop.pchirp.get_term() \n
		Sets the term of the chirp polynomial. \n
			:return: term: float Range: 0 to 32
		"""
		response = self._core.io.query_str('PULSe:MOP:PCHirp:TERM?')
		return Conversions.str_to_float(response)

	def set_term(self, term: float) -> None:
		"""SCPI: PULSe:MOP:PCHirp:TERM \n
		Snippet: driver.pulse.mop.pchirp.set_term(term = 1.0) \n
		Sets the term of the chirp polynomial. \n
			:param term: float Range: 0 to 32
		"""
		param = Conversions.decimal_value_to_str(term)
		self._core.io.write(f'PULSe:MOP:PCHirp:TERM {param}')

	def clone(self) -> 'Pchirp':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Pchirp(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
