from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Marker:
	"""Marker commands group definition. 4 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("marker", core, parent)

	@property
	def scenario(self):
		"""scenario commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_scenario'):
			from .Scenario import Scenario
			self._scenario = Scenario(self._core, self._cmd_group)
		return self._scenario

	def get_enable(self) -> bool:
		"""SCPI: SCENario:OUTPut:MARKer:ENABle \n
		Snippet: value: bool = driver.scenario.output.marker.get_enable() \n
		Enables that markers are considered by the generation of the output waveform file. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:OUTPut:MARKer:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SCENario:OUTPut:MARKer:ENABle \n
		Snippet: driver.scenario.output.marker.set_enable(enable = False) \n
		Enables that markers are considered by the generation of the output waveform file. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:OUTPut:MARKer:ENABle {param}')

	def get_flags(self) -> float:
		"""SCPI: SCENario:OUTPut:MARKer:FLAGs \n
		Snippet: value: float = driver.scenario.output.marker.get_flags() \n
		Enables up to four markers. \n
			:return: flags: int Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		response = self._core.io.query_str('SCENario:OUTPut:MARKer:FLAGs?')
		return Conversions.str_to_float(response)

	def set_flags(self, flags: float) -> None:
		"""SCPI: SCENario:OUTPut:MARKer:FLAGs \n
		Snippet: driver.scenario.output.marker.set_flags(flags = 1.0) \n
		Enables up to four markers. \n
			:param flags: int Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		param = Conversions.decimal_value_to_str(flags)
		self._core.io.write(f'SCENario:OUTPut:MARKer:FLAGs {param}')

	def clone(self) -> 'Marker':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Marker(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
