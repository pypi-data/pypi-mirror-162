from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Used:
	"""Used commands group definition. 7 total commands, 1 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("used", core, parent)

	@property
	def path(self):
		"""path commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_path'):
			from .Path import Path
			self._path = Path(self._core, self._cmd_group)
		return self._path

	def get_frequency(self) -> float:
		"""SCPI: CPANel:USED:FREQuency \n
		Snippet: value: float = driver.cpanel.used.get_frequency() \n
		Sets the RF frequency. \n
			:return: frequency: float
		"""
		response = self._core.io.query_str('CPANel:USED:FREQuency?')
		return Conversions.str_to_float(response)

	def set_frequency(self, frequency: float) -> None:
		"""SCPI: CPANel:USED:FREQuency \n
		Snippet: driver.cpanel.used.set_frequency(frequency = 1.0) \n
		Sets the RF frequency. \n
			:param frequency: float
		"""
		param = Conversions.decimal_value_to_str(frequency)
		self._core.io.write(f'CPANel:USED:FREQuency {param}')

	def get_level(self) -> float:
		"""SCPI: CPANel:USED:LEVel \n
		Snippet: value: float = driver.cpanel.used.get_level() \n
		Sets the RF level. \n
			:return: level: float
		"""
		response = self._core.io.query_str('CPANel:USED:LEVel?')
		return Conversions.str_to_float(response)

	def set_level(self, level: float) -> None:
		"""SCPI: CPANel:USED:LEVel \n
		Snippet: driver.cpanel.used.set_level(level = 1.0) \n
		Sets the RF level. \n
			:param level: float
		"""
		param = Conversions.decimal_value_to_str(level)
		self._core.io.write(f'CPANel:USED:LEVel {param}')

	def get_list_py(self) -> List[int]:
		"""SCPI: CPANel:USED:LIST \n
		Snippet: value: List[int] = driver.cpanel.used.get_list_py() \n
		Queries the names of the used/unused signal generators. \n
			:return: list_py: 'Instr#1','Instr#2',...
		"""
		response = self._core.io.query_bin_or_ascii_int_list('CPANel:USED:LIST?')
		return response

	def get_select(self) -> str:
		"""SCPI: CPANel:USED:SELect \n
		Snippet: value: str = driver.cpanel.used.get_select() \n
		Selects the element to which the subsequent commands apply. \n
			:return: select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Generator.Path.Antenna.listPy
		"""
		response = self._core.io.query_str('CPANel:USED:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: CPANel:USED:SELect \n
		Snippet: driver.cpanel.used.set_select(select = '1') \n
		Selects the element to which the subsequent commands apply. \n
			:param select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Generator.Path.Antenna.listPy
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'CPANel:USED:SELect {param}')

	def get_state(self) -> bool:
		"""SCPI: CPANel:USED:STATe \n
		Snippet: value: bool = driver.cpanel.used.get_state() \n
		Activates the RF output of the selected signal generator. \n
			:return: state: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('CPANel:USED:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, state: bool) -> None:
		"""SCPI: CPANel:USED:STATe \n
		Snippet: driver.cpanel.used.set_state(state = False) \n
		Activates the RF output of the selected signal generator. \n
			:param state: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'CPANel:USED:STATe {param}')

	def clone(self) -> 'Used':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Used(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
