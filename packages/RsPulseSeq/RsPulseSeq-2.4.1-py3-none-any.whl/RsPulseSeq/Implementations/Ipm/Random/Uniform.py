from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Uniform:
	"""Uniform commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("uniform", core, parent)

	def get_maximum(self) -> float:
		"""SCPI: IPM:RANDom:UNIForm:MAXimum \n
		Snippet: value: float = driver.ipm.random.uniform.get_maximum() \n
		Sets the range of the uniform distribution function. \n
			:return: maximum: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('IPM:RANDom:UNIForm:MAXimum?')
		return Conversions.str_to_float(response)

	def set_maximum(self, maximum: float) -> None:
		"""SCPI: IPM:RANDom:UNIForm:MAXimum \n
		Snippet: driver.ipm.random.uniform.set_maximum(maximum = 1.0) \n
		Sets the range of the uniform distribution function. \n
			:param maximum: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(maximum)
		self._core.io.write(f'IPM:RANDom:UNIForm:MAXimum {param}')

	def get_minimum(self) -> float:
		"""SCPI: IPM:RANDom:UNIForm:MINimum \n
		Snippet: value: float = driver.ipm.random.uniform.get_minimum() \n
		Sets the range of the uniform distribution function. \n
			:return: minimum: No help available
		"""
		response = self._core.io.query_str('IPM:RANDom:UNIForm:MINimum?')
		return Conversions.str_to_float(response)

	def set_minimum(self, minimum: float) -> None:
		"""SCPI: IPM:RANDom:UNIForm:MINimum \n
		Snippet: driver.ipm.random.uniform.set_minimum(minimum = 1.0) \n
		Sets the range of the uniform distribution function. \n
			:param minimum: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(minimum)
		self._core.io.write(f'IPM:RANDom:UNIForm:MINimum {param}')

	def get_step(self) -> float:
		"""SCPI: IPM:RANDom:UNIForm:STEP \n
		Snippet: value: float = driver.ipm.random.uniform.get_step() \n
		Sets the granularity of the uniform distribution function. \n
			:return: step: float Range: 1e-09 to 1e+09
		"""
		response = self._core.io.query_str('IPM:RANDom:UNIForm:STEP?')
		return Conversions.str_to_float(response)

	def set_step(self, step: float) -> None:
		"""SCPI: IPM:RANDom:UNIForm:STEP \n
		Snippet: driver.ipm.random.uniform.set_step(step = 1.0) \n
		Sets the granularity of the uniform distribution function. \n
			:param step: float Range: 1e-09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(step)
		self._core.io.write(f'IPM:RANDom:UNIForm:STEP {param}')
