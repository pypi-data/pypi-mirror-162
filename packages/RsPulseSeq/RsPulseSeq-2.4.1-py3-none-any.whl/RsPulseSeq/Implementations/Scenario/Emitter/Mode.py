from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Mode:
	"""Mode commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def get_beam(self) -> float:
		"""SCPI: SCENario:EMITter:MODE:BEAM \n
		Snippet: value: float = driver.scenario.emitter.mode.get_beam() \n
		Sets the used beam of the current mode. \n
			:return: beam: float Range: 1 to 32
		"""
		response = self._core.io.query_str('SCENario:EMITter:MODE:BEAM?')
		return Conversions.str_to_float(response)

	def set_beam(self, beam: float) -> None:
		"""SCPI: SCENario:EMITter:MODE:BEAM \n
		Snippet: driver.scenario.emitter.mode.set_beam(beam = 1.0) \n
		Sets the used beam of the current mode. \n
			:param beam: float Range: 1 to 32
		"""
		param = Conversions.decimal_value_to_str(beam)
		self._core.io.write(f'SCENario:EMITter:MODE:BEAM {param}')

	def get_value(self) -> float:
		"""SCPI: SCENario:EMITter:MODE \n
		Snippet: value: float = driver.scenario.emitter.mode.get_value() \n
		Set the emitter mode. \n
			:return: mode: float Range: 1 to 32
		"""
		response = self._core.io.query_str('SCENario:EMITter:MODE?')
		return Conversions.str_to_float(response)

	def set_value(self, mode: float) -> None:
		"""SCPI: SCENario:EMITter:MODE \n
		Snippet: driver.scenario.emitter.mode.set_value(mode = 1.0) \n
		Set the emitter mode. \n
			:param mode: float Range: 1 to 32
		"""
		param = Conversions.decimal_value_to_str(mode)
		self._core.io.write(f'SCENario:EMITter:MODE {param}')
