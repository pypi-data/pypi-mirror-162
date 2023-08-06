from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Unused:
	"""Unused commands group definition. 8 total commands, 1 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("unused", core, parent)

	@property
	def path(self):
		"""path commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_path'):
			from .Path import Path
			self._path = Path(self._core, self._cmd_group)
		return self._path

	def get_all(self) -> bool:
		"""SCPI: CPANel:UNUSed:ALL \n
		Snippet: value: bool = driver.cpanel.unused.get_all() \n
		Shows all unused signal generators. \n
			:return: all_py: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('CPANel:UNUSed:ALL?')
		return Conversions.str_to_bool(response)

	def set_all(self, all_py: bool) -> None:
		"""SCPI: CPANel:UNUSed:ALL \n
		Snippet: driver.cpanel.unused.set_all(all_py = False) \n
		Shows all unused signal generators. \n
			:param all_py: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(all_py)
		self._core.io.write(f'CPANel:UNUSed:ALL {param}')

	def get_frequency(self) -> float:
		"""SCPI: CPANel:UNUSed:FREQuency \n
		Snippet: value: float = driver.cpanel.unused.get_frequency() \n
		Sets the RF frequency. \n
			:return: frequency: float
		"""
		response = self._core.io.query_str('CPANel:UNUSed:FREQuency?')
		return Conversions.str_to_float(response)

	def set_frequency(self, frequency: float) -> None:
		"""SCPI: CPANel:UNUSed:FREQuency \n
		Snippet: driver.cpanel.unused.set_frequency(frequency = 1.0) \n
		Sets the RF frequency. \n
			:param frequency: float
		"""
		param = Conversions.decimal_value_to_str(frequency)
		self._core.io.write(f'CPANel:UNUSed:FREQuency {param}')

	def get_level(self) -> float:
		"""SCPI: CPANel:UNUSed:LEVel \n
		Snippet: value: float = driver.cpanel.unused.get_level() \n
		Sets the RF level. \n
			:return: level: float
		"""
		response = self._core.io.query_str('CPANel:UNUSed:LEVel?')
		return Conversions.str_to_float(response)

	def set_level(self, level: float) -> None:
		"""SCPI: CPANel:UNUSed:LEVel \n
		Snippet: driver.cpanel.unused.set_level(level = 1.0) \n
		Sets the RF level. \n
			:param level: float
		"""
		param = Conversions.decimal_value_to_str(level)
		self._core.io.write(f'CPANel:UNUSed:LEVel {param}')

	def get_list_py(self) -> List[int]:
		"""SCPI: CPANel:UNUSed:LIST \n
		Snippet: value: List[int] = driver.cpanel.unused.get_list_py() \n
		Queries the names of the used/unused signal generators. \n
			:return: list_py: 'Instr#1','Instr#2',...
		"""
		response = self._core.io.query_bin_or_ascii_int_list('CPANel:UNUSed:LIST?')
		return response

	def get_select(self) -> str:
		"""SCPI: CPANel:UNUSed:SELect \n
		Snippet: value: str = driver.cpanel.unused.get_select() \n
		Selects the element to which the subsequent commands apply. \n
			:return: select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Generator.Path.Antenna.listPy
		"""
		response = self._core.io.query_str('CPANel:UNUSed:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: CPANel:UNUSed:SELect \n
		Snippet: driver.cpanel.unused.set_select(select = '1') \n
		Selects the element to which the subsequent commands apply. \n
			:param select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Generator.Path.Antenna.listPy
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'CPANel:UNUSed:SELect {param}')

	def get_state(self) -> bool:
		"""SCPI: CPANel:UNUSed:STATe \n
		Snippet: value: bool = driver.cpanel.unused.get_state() \n
		Activates the RF output of the selected signal generator. \n
			:return: state: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('CPANel:UNUSed:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, state: bool) -> None:
		"""SCPI: CPANel:UNUSed:STATe \n
		Snippet: driver.cpanel.unused.set_state(state = False) \n
		Activates the RF output of the selected signal generator. \n
			:param state: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'CPANel:UNUSed:STATe {param}')

	def clone(self) -> 'Unused':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Unused(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
