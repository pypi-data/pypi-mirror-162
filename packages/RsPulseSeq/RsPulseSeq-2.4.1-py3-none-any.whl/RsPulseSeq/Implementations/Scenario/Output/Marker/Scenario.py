from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Scenario:
	"""Scenario commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("scenario", core, parent)

	def get_duration(self) -> float:
		"""SCPI: SCENario:OUTPut:MARKer:SCENario:DURation \n
		Snippet: value: float = driver.scenario.output.marker.scenario.get_duration() \n
		Sets the duration of the scenario marker. \n
			:return: duration: float Range: 0 to 1, Unit: sec
		"""
		response = self._core.io.query_str('SCENario:OUTPut:MARKer:SCENario:DURation?')
		return Conversions.str_to_float(response)

	def set_duration(self, duration: float) -> None:
		"""SCPI: SCENario:OUTPut:MARKer:SCENario:DURation \n
		Snippet: driver.scenario.output.marker.scenario.set_duration(duration = 1.0) \n
		Sets the duration of the scenario marker. \n
			:param duration: float Range: 0 to 1, Unit: sec
		"""
		param = Conversions.decimal_value_to_str(duration)
		self._core.io.write(f'SCENario:OUTPut:MARKer:SCENario:DURation {param}')

	def get_enable(self) -> bool:
		"""SCPI: SCENario:OUTPut:MARKer:SCENario:ENABle \n
		Snippet: value: bool = driver.scenario.output.marker.scenario.get_enable() \n
		Enables an additional marker, that is held high from the scenario start until the duration, selected with the command
		method RsPulseSeq.Scenario.Output.Marker.Scenario.duration. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:OUTPut:MARKer:SCENario:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SCENario:OUTPut:MARKer:SCENario:ENABle \n
		Snippet: driver.scenario.output.marker.scenario.set_enable(enable = False) \n
		Enables an additional marker, that is held high from the scenario start until the duration, selected with the command
		method RsPulseSeq.Scenario.Output.Marker.Scenario.duration. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:OUTPut:MARKer:SCENario:ENABle {param}')
