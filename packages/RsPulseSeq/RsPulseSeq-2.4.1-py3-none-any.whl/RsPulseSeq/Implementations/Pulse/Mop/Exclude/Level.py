from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Level:
	"""Level commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("level", core, parent)

	def get_start(self) -> float:
		"""SCPI: PULSe:MOP:EXCLude:LEVel:STARt \n
		Snippet: value: float = driver.pulse.mop.exclude.level.get_start() \n
		Sets the threshold levels at the beginning and the end of a pulse for the modulation to be excluded. \n
			:return: start: No help available
		"""
		response = self._core.io.query_str('PULSe:MOP:EXCLude:LEVel:STARt?')
		return Conversions.str_to_float(response)

	def set_start(self, start: float) -> None:
		"""SCPI: PULSe:MOP:EXCLude:LEVel:STARt \n
		Snippet: driver.pulse.mop.exclude.level.set_start(start = 1.0) \n
		Sets the threshold levels at the beginning and the end of a pulse for the modulation to be excluded. \n
			:param start: float Range: 0 to 100
		"""
		param = Conversions.decimal_value_to_str(start)
		self._core.io.write(f'PULSe:MOP:EXCLude:LEVel:STARt {param}')

	def get_stop(self) -> float:
		"""SCPI: PULSe:MOP:EXCLude:LEVel:STOP \n
		Snippet: value: float = driver.pulse.mop.exclude.level.get_stop() \n
		Sets the threshold levels at the beginning and the end of a pulse for the modulation to be excluded. \n
			:return: stop: float Range: 0 to 100
		"""
		response = self._core.io.query_str('PULSe:MOP:EXCLude:LEVel:STOP?')
		return Conversions.str_to_float(response)

	def set_stop(self, stop: float) -> None:
		"""SCPI: PULSe:MOP:EXCLude:LEVel:STOP \n
		Snippet: driver.pulse.mop.exclude.level.set_stop(stop = 1.0) \n
		Sets the threshold levels at the beginning and the end of a pulse for the modulation to be excluded. \n
			:param stop: float Range: 0 to 100
		"""
		param = Conversions.decimal_value_to_str(stop)
		self._core.io.write(f'PULSe:MOP:EXCLude:LEVel:STOP {param}')
