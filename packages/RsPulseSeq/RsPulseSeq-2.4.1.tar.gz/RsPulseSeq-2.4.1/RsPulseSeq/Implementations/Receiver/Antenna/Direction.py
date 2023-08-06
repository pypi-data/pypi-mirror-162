from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Direction:
	"""Direction commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("direction", core, parent)

	def get_away(self) -> bool:
		"""SCPI: RECeiver:ANTenna:DIRection:AWAY \n
		Snippet: value: bool = driver.receiver.antenna.direction.get_away() \n
		Sets the azimuth automatically, so that the beam axis is radial to the receiver origin. \n
			:return: away: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:DIRection:AWAY?')
		return Conversions.str_to_bool(response)

	def set_away(self, away: bool) -> None:
		"""SCPI: RECeiver:ANTenna:DIRection:AWAY \n
		Snippet: driver.receiver.antenna.direction.set_away(away = False) \n
		Sets the azimuth automatically, so that the beam axis is radial to the receiver origin. \n
			:param away: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(away)
		self._core.io.write(f'RECeiver:ANTenna:DIRection:AWAY {param}')

	def get_azimuth(self) -> float:
		"""SCPI: RECeiver:ANTenna:DIRection:AZIMuth \n
		Snippet: value: float = driver.receiver.antenna.direction.get_azimuth() \n
		Turns the antenna beam axis. \n
			:return: azimuth: float Range: 0 to 360
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:DIRection:AZIMuth?')
		return Conversions.str_to_float(response)

	def set_azimuth(self, azimuth: float) -> None:
		"""SCPI: RECeiver:ANTenna:DIRection:AZIMuth \n
		Snippet: driver.receiver.antenna.direction.set_azimuth(azimuth = 1.0) \n
		Turns the antenna beam axis. \n
			:param azimuth: float Range: 0 to 360
		"""
		param = Conversions.decimal_value_to_str(azimuth)
		self._core.io.write(f'RECeiver:ANTenna:DIRection:AZIMuth {param}')

	def get_elevation(self) -> float:
		"""SCPI: RECeiver:ANTenna:DIRection:ELEVation \n
		Snippet: value: float = driver.receiver.antenna.direction.get_elevation() \n
		Turns the antenna beam axis. \n
			:return: elevation: float Range: -90 to 90
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:DIRection:ELEVation?')
		return Conversions.str_to_float(response)

	def set_elevation(self, elevation: float) -> None:
		"""SCPI: RECeiver:ANTenna:DIRection:ELEVation \n
		Snippet: driver.receiver.antenna.direction.set_elevation(elevation = 1.0) \n
		Turns the antenna beam axis. \n
			:param elevation: float Range: -90 to 90
		"""
		param = Conversions.decimal_value_to_str(elevation)
		self._core.io.write(f'RECeiver:ANTenna:DIRection:ELEVation {param}')
