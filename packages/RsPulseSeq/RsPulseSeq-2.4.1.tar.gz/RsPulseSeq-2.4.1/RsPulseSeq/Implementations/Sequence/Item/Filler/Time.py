from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Time:
	"""Time commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("time", core, parent)

	def get_equation(self) -> str:
		"""SCPI: SEQuence:ITEM:FILLer:TIME:EQUation \n
		Snippet: value: str = driver.sequence.item.filler.time.get_equation() \n
		Sets the filler duration as an equation. \n
			:return: equation: string
		"""
		response = self._core.io.query_str('SEQuence:ITEM:FILLer:TIME:EQUation?')
		return trim_str_response(response)

	def set_equation(self, equation: str) -> None:
		"""SCPI: SEQuence:ITEM:FILLer:TIME:EQUation \n
		Snippet: driver.sequence.item.filler.time.set_equation(equation = '1') \n
		Sets the filler duration as an equation. \n
			:param equation: string
		"""
		param = Conversions.value_to_quoted_str(equation)
		self._core.io.write(f'SEQuence:ITEM:FILLer:TIME:EQUation {param}')

	def get_fixed(self) -> float:
		"""SCPI: SEQuence:ITEM:FILLer:TIME:FIXed \n
		Snippet: value: float = driver.sequence.item.filler.time.get_fixed() \n
		Sets the duration of the filler. \n
			:return: fixed: float Range: 0 to 1e+09, Unit: sec
		"""
		response = self._core.io.query_str('SEQuence:ITEM:FILLer:TIME:FIXed?')
		return Conversions.str_to_float(response)

	def set_fixed(self, fixed: float) -> None:
		"""SCPI: SEQuence:ITEM:FILLer:TIME:FIXed \n
		Snippet: driver.sequence.item.filler.time.set_fixed(fixed = 1.0) \n
		Sets the duration of the filler. \n
			:param fixed: float Range: 0 to 1e+09, Unit: sec
		"""
		param = Conversions.decimal_value_to_str(fixed)
		self._core.io.write(f'SEQuence:ITEM:FILLer:TIME:FIXed {param}')

	# noinspection PyTypeChecker
	def get_value(self) -> enums.FillerTime:
		"""SCPI: SEQuence:ITEM:FILLer:TIME \n
		Snippet: value: enums.FillerTime = driver.sequence.item.filler.time.get_value() \n
		Defines the way the duration is defined. \n
			:return: time: FIXed| EQUation
		"""
		response = self._core.io.query_str('SEQuence:ITEM:FILLer:TIME?')
		return Conversions.str_to_scalar_enum(response, enums.FillerTime)

	def set_value(self, time: enums.FillerTime) -> None:
		"""SCPI: SEQuence:ITEM:FILLer:TIME \n
		Snippet: driver.sequence.item.filler.time.set_value(time = enums.FillerTime.EQUation) \n
		Defines the way the duration is defined. \n
			:param time: FIXed| EQUation
		"""
		param = Conversions.enum_scalar_to_str(time, enums.FillerTime)
		self._core.io.write(f'SEQuence:ITEM:FILLer:TIME {param}')
