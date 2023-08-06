from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Pstep:
	"""Pstep commands group definition. 4 total commands, 1 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pstep", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	def get_count(self) -> float:
		"""SCPI: SCENario:LOCalized:LOCation:PSTep:COUNt \n
		Snippet: value: float = driver.scenario.localized.location.pstep.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('SCENario:LOCalized:LOCation:PSTep:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: SCENario:LOCalized:LOCation:PSTep:DELete \n
		Snippet: driver.scenario.localized.location.pstep.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'SCENario:LOCalized:LOCation:PSTep:DELete {param}')

	def get_select(self) -> float:
		"""SCPI: SCENario:LOCalized:LOCation:PSTep:SELect \n
		Snippet: value: float = driver.scenario.localized.location.pstep.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('SCENario:LOCalized:LOCation:PSTep:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: SCENario:LOCalized:LOCation:PSTep:SELect \n
		Snippet: driver.scenario.localized.location.pstep.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'SCENario:LOCalized:LOCation:PSTep:SELect {param}')

	def clone(self) -> 'Pstep':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Pstep(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
