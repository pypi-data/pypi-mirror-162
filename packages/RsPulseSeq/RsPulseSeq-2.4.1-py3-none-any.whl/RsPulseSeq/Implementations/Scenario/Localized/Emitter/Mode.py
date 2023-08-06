from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Mode:
	"""Mode commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def get_beam(self) -> float:
		"""SCPI: SCENario:LOCalized:EMITter:MODE:BEAM \n
		Snippet: value: float = driver.scenario.localized.emitter.mode.get_beam() \n
		Sets the used beam of the current mode. \n
			:return: beam: float Range: 1 to 32
		"""
		response = self._core.io.query_str('SCENario:LOCalized:EMITter:MODE:BEAM?')
		return Conversions.str_to_float(response)

	def set_beam(self, beam: float) -> None:
		"""SCPI: SCENario:LOCalized:EMITter:MODE:BEAM \n
		Snippet: driver.scenario.localized.emitter.mode.set_beam(beam = 1.0) \n
		Sets the used beam of the current mode. \n
			:param beam: float Range: 1 to 32
		"""
		param = Conversions.decimal_value_to_str(beam)
		self._core.io.write(f'SCENario:LOCalized:EMITter:MODE:BEAM {param}')

	def get_track_rec(self) -> bool:
		"""SCPI: SCENario:LOCalized:EMITter:MODE:TRACkrec \n
		Snippet: value: bool = driver.scenario.localized.emitter.mode.get_track_rec() \n
		If enabled, the scan follows the receiver automatically. \n
			:return: track_rec: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:LOCalized:EMITter:MODE:TRACkrec?')
		return Conversions.str_to_bool(response)

	def set_track_rec(self, track_rec: bool) -> None:
		"""SCPI: SCENario:LOCalized:EMITter:MODE:TRACkrec \n
		Snippet: driver.scenario.localized.emitter.mode.set_track_rec(track_rec = False) \n
		If enabled, the scan follows the receiver automatically. \n
			:param track_rec: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(track_rec)
		self._core.io.write(f'SCENario:LOCalized:EMITter:MODE:TRACkrec {param}')

	def get_value(self) -> float:
		"""SCPI: SCENario:LOCalized:EMITter:MODE \n
		Snippet: value: float = driver.scenario.localized.emitter.mode.get_value() \n
		Set the emitter mode. \n
			:return: mode: float Range: 1 to 32
		"""
		response = self._core.io.query_str('SCENario:LOCalized:EMITter:MODE?')
		return Conversions.str_to_float(response)

	def set_value(self, mode: float) -> None:
		"""SCPI: SCENario:LOCalized:EMITter:MODE \n
		Snippet: driver.scenario.localized.emitter.mode.set_value(mode = 1.0) \n
		Set the emitter mode. \n
			:param mode: float Range: 1 to 32
		"""
		param = Conversions.decimal_value_to_str(mode)
		self._core.io.write(f'SCENario:LOCalized:EMITter:MODE {param}')
