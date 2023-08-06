from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Group:
	"""Group commands group definition. 8 total commands, 1 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("group", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	def get_alias(self) -> str:
		"""SCPI: SCENario:CPDW:GROup:ALIas \n
		Snippet: value: str = driver.scenario.cpdw.group.get_alias() \n
		Sets an alias name for the selected interleaving group. See also method RsPulseSeq.Assignment.Group.select. \n
			:return: alias: string
		"""
		response = self._core.io.query_str('SCENario:CPDW:GROup:ALIas?')
		return trim_str_response(response)

	def set_alias(self, alias: str) -> None:
		"""SCPI: SCENario:CPDW:GROup:ALIas \n
		Snippet: driver.scenario.cpdw.group.set_alias(alias = '1') \n
		Sets an alias name for the selected interleaving group. See also method RsPulseSeq.Assignment.Group.select. \n
			:param alias: string
		"""
		param = Conversions.value_to_quoted_str(alias)
		self._core.io.write(f'SCENario:CPDW:GROup:ALIas {param}')

	def get_catalog(self) -> str:
		"""SCPI: SCENario:CPDW:GROup:CATalog \n
		Snippet: value: str = driver.scenario.cpdw.group.get_catalog() \n
		Queries the alias names of the configured interleaving groups. \n
			:return: catalog: string A list of coma-separated alias names.
		"""
		response = self._core.io.query_str('SCENario:CPDW:GROup:CATalog?')
		return trim_str_response(response)

	def clear(self) -> None:
		"""SCPI: SCENario:CPDW:GROup:CLEar \n
		Snippet: driver.scenario.cpdw.group.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'SCENario:CPDW:GROup:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:CPDW:GROup:CLEar \n
		Snippet: driver.scenario.cpdw.group.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:CPDW:GROup:CLEar', opc_timeout_ms)

	def get_count(self) -> float:
		"""SCPI: SCENario:CPDW:GROup:COUNt \n
		Snippet: value: float = driver.scenario.cpdw.group.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('SCENario:CPDW:GROup:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: SCENario:CPDW:GROup:DELete \n
		Snippet: driver.scenario.cpdw.group.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'SCENario:CPDW:GROup:DELete {param}')

	def get_select(self) -> float:
		"""SCPI: SCENario:CPDW:GROup:SELect \n
		Snippet: value: float = driver.scenario.cpdw.group.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('SCENario:CPDW:GROup:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: SCENario:CPDW:GROup:SELect \n
		Snippet: driver.scenario.cpdw.group.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'SCENario:CPDW:GROup:SELect {param}')

	def get_value(self) -> str:
		"""SCPI: SCENario:CPDW:GROup \n
		Snippet: value: str = driver.scenario.cpdw.group.get_value() \n
		Assigns the emitter to one of the available interleaving groups. \n
			:return: group: string Query a list of the alias names of the existing interleaving groups with the command method RsPulseSeq.Scenario.Cpdw.Group.catalog.
		"""
		response = self._core.io.query_str('SCENario:CPDW:GROup?')
		return trim_str_response(response)

	def set_value(self, group: str) -> None:
		"""SCPI: SCENario:CPDW:GROup \n
		Snippet: driver.scenario.cpdw.group.set_value(group = '1') \n
		Assigns the emitter to one of the available interleaving groups. \n
			:param group: string Query a list of the alias names of the existing interleaving groups with the command method RsPulseSeq.Scenario.Cpdw.Group.catalog.
		"""
		param = Conversions.value_to_quoted_str(group)
		self._core.io.write(f'SCENario:CPDW:GROup {param}')

	def clone(self) -> 'Group':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Group(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
