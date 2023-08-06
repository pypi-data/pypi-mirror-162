from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Waveform:
	"""Waveform commands group definition. 6 total commands, 0 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("waveform", core, parent)

	def get_antenna(self) -> str:
		"""SCPI: SCENario:DF:WAVeform:ANTenna \n
		Snippet: value: str = driver.scenario.df.waveform.get_antenna() \n
		Assigns an existing antenna pattern, see method RsPulseSeq.Antenna.catalog. \n
			:return: antenna: string
		"""
		response = self._core.io.query_str('SCENario:DF:WAVeform:ANTenna?')
		return trim_str_response(response)

	def set_antenna(self, antenna: str) -> None:
		"""SCPI: SCENario:DF:WAVeform:ANTenna \n
		Snippet: driver.scenario.df.waveform.set_antenna(antenna = '1') \n
		Assigns an existing antenna pattern, see method RsPulseSeq.Antenna.catalog. \n
			:param antenna: string
		"""
		param = Conversions.value_to_quoted_str(antenna)
		self._core.io.write(f'SCENario:DF:WAVeform:ANTenna {param}')

	def get_eirp(self) -> float:
		"""SCPI: SCENario:DF:WAVeform:EIRP \n
		Snippet: value: float = driver.scenario.df.waveform.get_eirp() \n
		Sets the of the interferer. \n
			:return: eirp: float Range: -200 to 200
		"""
		response = self._core.io.query_str('SCENario:DF:WAVeform:EIRP?')
		return Conversions.str_to_float(response)

	def set_eirp(self, eirp: float) -> None:
		"""SCPI: SCENario:DF:WAVeform:EIRP \n
		Snippet: driver.scenario.df.waveform.set_eirp(eirp = 1.0) \n
		Sets the of the interferer. \n
			:param eirp: float Range: -200 to 200
		"""
		param = Conversions.decimal_value_to_str(eirp)
		self._core.io.write(f'SCENario:DF:WAVeform:EIRP {param}')

	def get_frequency(self) -> float:
		"""SCPI: SCENario:DF:WAVeform:FREQuency \n
		Snippet: value: float = driver.scenario.df.waveform.get_frequency() \n
		Sets the frequency of the emitter. \n
			:return: frequency: float Range: 1000 to 4.4e+10
		"""
		response = self._core.io.query_str('SCENario:DF:WAVeform:FREQuency?')
		return Conversions.str_to_float(response)

	def set_frequency(self, frequency: float) -> None:
		"""SCPI: SCENario:DF:WAVeform:FREQuency \n
		Snippet: driver.scenario.df.waveform.set_frequency(frequency = 1.0) \n
		Sets the frequency of the emitter. \n
			:param frequency: float Range: 1000 to 4.4e+10
		"""
		param = Conversions.decimal_value_to_str(frequency)
		self._core.io.write(f'SCENario:DF:WAVeform:FREQuency {param}')

	def get_level(self) -> float:
		"""SCPI: SCENario:DF:WAVeform:LEVel \n
		Snippet: value: float = driver.scenario.df.waveform.get_level() \n
		Sets the of the interferer. \n
			:return: level: No help available
		"""
		response = self._core.io.query_str('SCENario:DF:WAVeform:LEVel?')
		return Conversions.str_to_float(response)

	def set_level(self, level: float) -> None:
		"""SCPI: SCENario:DF:WAVeform:LEVel \n
		Snippet: driver.scenario.df.waveform.set_level(level = 1.0) \n
		Sets the of the interferer. \n
			:param level: float Range: -200 to 200
		"""
		param = Conversions.decimal_value_to_str(level)
		self._core.io.write(f'SCENario:DF:WAVeform:LEVel {param}')

	def get_scan(self) -> str:
		"""SCPI: SCENario:DF:WAVeform:SCAN \n
		Snippet: value: str = driver.scenario.df.waveform.get_scan() \n
		Assigns an existing antenna scan, see method RsPulseSeq.Scan.catalog. \n
			:return: scan: string
		"""
		response = self._core.io.query_str('SCENario:DF:WAVeform:SCAN?')
		return trim_str_response(response)

	def set_scan(self, scan: str) -> None:
		"""SCPI: SCENario:DF:WAVeform:SCAN \n
		Snippet: driver.scenario.df.waveform.set_scan(scan = '1') \n
		Assigns an existing antenna scan, see method RsPulseSeq.Scan.catalog. \n
			:param scan: string
		"""
		param = Conversions.value_to_quoted_str(scan)
		self._core.io.write(f'SCENario:DF:WAVeform:SCAN {param}')

	def get_value(self) -> str:
		"""SCPI: SCENario:DF:WAVeform \n
		Snippet: value: str = driver.scenario.df.waveform.get_value() \n
		Assigns an existing emitter or an existing waveform, see method RsPulseSeq.Waveform.catalog and method RsPulseSeq.Emitter.
		catalog. \n
			:return: waveform: string
		"""
		response = self._core.io.query_str('SCENario:DF:WAVeform?')
		return trim_str_response(response)

	def set_value(self, waveform: str) -> None:
		"""SCPI: SCENario:DF:WAVeform \n
		Snippet: driver.scenario.df.waveform.set_value(waveform = '1') \n
		Assigns an existing emitter or an existing waveform, see method RsPulseSeq.Waveform.catalog and method RsPulseSeq.Emitter.
		catalog. \n
			:param waveform: string
		"""
		param = Conversions.value_to_quoted_str(waveform)
		self._core.io.write(f'SCENario:DF:WAVeform {param}')
