from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Time:
	"""Time commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("time", core, parent)

	def get_start(self) -> float:
		"""SCPI: PULSe:MOP:EXCLude:TIME:STARt \n
		Snippet: value: float = driver.pulse.mop.exclude.time.get_start() \n
		Sets a time span to be excluded at the beginning and at the end of the pulse. \n
			:return: start: No help available
		"""
		response = self._core.io.query_str('PULSe:MOP:EXCLude:TIME:STARt?')
		return Conversions.str_to_float(response)

	def set_start(self, start: float) -> None:
		"""SCPI: PULSe:MOP:EXCLude:TIME:STARt \n
		Snippet: driver.pulse.mop.exclude.time.set_start(start = 1.0) \n
		Sets a time span to be excluded at the beginning and at the end of the pulse. \n
			:param start: float Range: 0 to 5e-07
		"""
		param = Conversions.decimal_value_to_str(start)
		self._core.io.write(f'PULSe:MOP:EXCLude:TIME:STARt {param}')

	def get_stop(self) -> float:
		"""SCPI: PULSe:MOP:EXCLude:TIME:STOP \n
		Snippet: value: float = driver.pulse.mop.exclude.time.get_stop() \n
		Sets a time span to be excluded at the beginning and at the end of the pulse. \n
			:return: stop: float Range: 0 to 5e-07
		"""
		response = self._core.io.query_str('PULSe:MOP:EXCLude:TIME:STOP?')
		return Conversions.str_to_float(response)

	def set_stop(self, stop: float) -> None:
		"""SCPI: PULSe:MOP:EXCLude:TIME:STOP \n
		Snippet: driver.pulse.mop.exclude.time.set_stop(stop = 1.0) \n
		Sets a time span to be excluded at the beginning and at the end of the pulse. \n
			:param stop: float Range: 0 to 5e-07
		"""
		param = Conversions.decimal_value_to_str(stop)
		self._core.io.write(f'PULSe:MOP:EXCLude:TIME:STOP {param}')
