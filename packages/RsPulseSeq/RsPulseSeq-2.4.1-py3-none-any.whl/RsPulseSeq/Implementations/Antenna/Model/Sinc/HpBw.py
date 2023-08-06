from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HpBw:
	"""HpBw commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("hpBw", core, parent)

	def get_azimuth(self) -> float:
		"""SCPI: ANTenna:MODel:SINC:HPBW:AZIMuth \n
		Snippet: value: float = driver.antenna.model.sinc.hpBw.get_azimuth() \n
		Sets the Half-Power Beam Width in azimuth and elevation direction for the Gaussian and Sin(x) /x antennas. \n
			:return: azimuth: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:SINC:HPBW:AZIMuth?')
		return Conversions.str_to_float(response)

	def set_azimuth(self, azimuth: float) -> None:
		"""SCPI: ANTenna:MODel:SINC:HPBW:AZIMuth \n
		Snippet: driver.antenna.model.sinc.hpBw.set_azimuth(azimuth = 1.0) \n
		Sets the Half-Power Beam Width in azimuth and elevation direction for the Gaussian and Sin(x) /x antennas. \n
			:param azimuth: float Range: 0.1 to 45, Unit: degree
		"""
		param = Conversions.decimal_value_to_str(azimuth)
		self._core.io.write(f'ANTenna:MODel:SINC:HPBW:AZIMuth {param}')

	def get_elevation(self) -> float:
		"""SCPI: ANTenna:MODel:SINC:HPBW:ELEVation \n
		Snippet: value: float = driver.antenna.model.sinc.hpBw.get_elevation() \n
		Sets the Half-Power Beam Width in azimuth and elevation direction for the Gaussian and Sin(x) /x antennas. \n
			:return: elevation: float Range: 0.1 to 45, Unit: degree
		"""
		response = self._core.io.query_str('ANTenna:MODel:SINC:HPBW:ELEVation?')
		return Conversions.str_to_float(response)

	def set_elevation(self, elevation: float) -> None:
		"""SCPI: ANTenna:MODel:SINC:HPBW:ELEVation \n
		Snippet: driver.antenna.model.sinc.hpBw.set_elevation(elevation = 1.0) \n
		Sets the Half-Power Beam Width in azimuth and elevation direction for the Gaussian and Sin(x) /x antennas. \n
			:param elevation: float Range: 0.1 to 45, Unit: degree
		"""
		param = Conversions.decimal_value_to_str(elevation)
		self._core.io.write(f'ANTenna:MODel:SINC:HPBW:ELEVation {param}')
