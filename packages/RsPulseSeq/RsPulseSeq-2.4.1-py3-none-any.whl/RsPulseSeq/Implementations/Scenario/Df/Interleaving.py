from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Interleaving:
	"""Interleaving commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("interleaving", core, parent)

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.InterleaveMode:
		"""SCPI: SCENario:DF:INTerleaving:MODE \n
		Snippet: value: enums.InterleaveMode = driver.scenario.df.interleaving.get_mode() \n
		Select the mode for interleaving. \n
			:return: mode: DROP| MERGe DROP Interleaving uses a priority-based dropping algorithm. MERGE Emitters or PDW lists are merged into multiple output files using groups.
		"""
		response = self._core.io.query_str('SCENario:DF:INTerleaving:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.InterleaveMode)

	def set_mode(self, mode: enums.InterleaveMode) -> None:
		"""SCPI: SCENario:DF:INTerleaving:MODE \n
		Snippet: driver.scenario.df.interleaving.set_mode(mode = enums.InterleaveMode.DROP) \n
		Select the mode for interleaving. \n
			:param mode: DROP| MERGe DROP Interleaving uses a priority-based dropping algorithm. MERGE Emitters or PDW lists are merged into multiple output files using groups.
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.InterleaveMode)
		self._core.io.write(f'SCENario:DF:INTerleaving:MODE {param}')

	def get_freq_agility(self) -> bool:
		"""SCPI: SCENario:DF:INTerleaving:FREQagility \n
		Snippet: value: bool = driver.scenario.df.interleaving.get_freq_agility() \n
		Enables frequency agility in interleaving. Requires R&S SMW with firmware version 5.xx.xxx and higher. To query the
		installed firmware version of the selected instrument, use the command method RsPulseSeq.Instrument.firmware. \n
			:return: freq_agility: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:DF:INTerleaving:FREQagility?')
		return Conversions.str_to_bool(response)

	def set_freq_agility(self, freq_agility: bool) -> None:
		"""SCPI: SCENario:DF:INTerleaving:FREQagility \n
		Snippet: driver.scenario.df.interleaving.set_freq_agility(freq_agility = False) \n
		Enables frequency agility in interleaving. Requires R&S SMW with firmware version 5.xx.xxx and higher. To query the
		installed firmware version of the selected instrument, use the command method RsPulseSeq.Instrument.firmware. \n
			:param freq_agility: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(freq_agility)
		self._core.io.write(f'SCENario:DF:INTerleaving:FREQagility {param}')

	def get_value(self) -> bool:
		"""SCPI: SCENario:DF:INTerleaving \n
		Snippet: value: bool = driver.scenario.df.interleaving.get_value() \n
		If enabled, multiple PDW lists are interleaved into a single output file using a priority-based dropping algorithm. Set
		the priority with the command method RsPulseSeq.Scenario.Cpdw.priority. \n
			:return: interleaving: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:DF:INTerleaving?')
		return Conversions.str_to_bool(response)

	def set_value(self, interleaving: bool) -> None:
		"""SCPI: SCENario:DF:INTerleaving \n
		Snippet: driver.scenario.df.interleaving.set_value(interleaving = False) \n
		If enabled, multiple PDW lists are interleaved into a single output file using a priority-based dropping algorithm. Set
		the priority with the command method RsPulseSeq.Scenario.Cpdw.priority. \n
			:param interleaving: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(interleaving)
		self._core.io.write(f'SCENario:DF:INTerleaving {param}')
