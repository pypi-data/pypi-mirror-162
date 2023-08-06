from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Offset:
	"""Offset commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("offset", core, parent)

	def get_azimuth(self) -> float:
		"""SCPI: EMITter:MODE:BEAM:OFFSet:AZIMuth \n
		Snippet: value: float = driver.emitter.mode.beam.offset.get_azimuth() \n
		Sets the Azimuth value for the beam offset. \n
			:return: azimuth: float Range: 0 to 360
		"""
		response = self._core.io.query_str('EMITter:MODE:BEAM:OFFSet:AZIMuth?')
		return Conversions.str_to_float(response)

	def set_azimuth(self, azimuth: float) -> None:
		"""SCPI: EMITter:MODE:BEAM:OFFSet:AZIMuth \n
		Snippet: driver.emitter.mode.beam.offset.set_azimuth(azimuth = 1.0) \n
		Sets the Azimuth value for the beam offset. \n
			:param azimuth: float Range: 0 to 360
		"""
		param = Conversions.decimal_value_to_str(azimuth)
		self._core.io.write(f'EMITter:MODE:BEAM:OFFSet:AZIMuth {param}')

	def get_elevation(self) -> float:
		"""SCPI: EMITter:MODE:BEAM:OFFSet:ELEVation \n
		Snippet: value: float = driver.emitter.mode.beam.offset.get_elevation() \n
		Offsets the position of the beam in both the azimuth or elevation. \n
			:return: elevation: float Range: -90 to 90
		"""
		response = self._core.io.query_str('EMITter:MODE:BEAM:OFFSet:ELEVation?')
		return Conversions.str_to_float(response)

	def set_elevation(self, elevation: float) -> None:
		"""SCPI: EMITter:MODE:BEAM:OFFSet:ELEVation \n
		Snippet: driver.emitter.mode.beam.offset.set_elevation(elevation = 1.0) \n
		Offsets the position of the beam in both the azimuth or elevation. \n
			:param elevation: float Range: -90 to 90
		"""
		param = Conversions.decimal_value_to_str(elevation)
		self._core.io.write(f'EMITter:MODE:BEAM:OFFSet:ELEVation {param}')

	def get_frequency(self) -> float:
		"""SCPI: EMITter:MODE:BEAM:OFFSet:FREQuency \n
		Snippet: value: float = driver.emitter.mode.beam.offset.get_frequency() \n
		Offsets the frequency of the beam. \n
			:return: frequency: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('EMITter:MODE:BEAM:OFFSet:FREQuency?')
		return Conversions.str_to_float(response)

	def set_frequency(self, frequency: float) -> None:
		"""SCPI: EMITter:MODE:BEAM:OFFSet:FREQuency \n
		Snippet: driver.emitter.mode.beam.offset.set_frequency(frequency = 1.0) \n
		Offsets the frequency of the beam. \n
			:param frequency: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(frequency)
		self._core.io.write(f'EMITter:MODE:BEAM:OFFSet:FREQuency {param}')
