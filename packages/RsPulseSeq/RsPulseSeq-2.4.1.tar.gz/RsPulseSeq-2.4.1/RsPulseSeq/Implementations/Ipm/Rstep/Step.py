from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Step:
	"""Step commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("step", core, parent)

	def get_maximum(self) -> float:
		"""SCPI: IPM:RSTep:STEP:MAXimum \n
		Snippet: value: float = driver.ipm.rstep.step.get_maximum() \n
		Sets the step size range. \n
			:return: maximum: float Range: 0.1 to 0.5
		"""
		response = self._core.io.query_str('IPM:RSTep:STEP:MAXimum?')
		return Conversions.str_to_float(response)

	def set_maximum(self, maximum: float) -> None:
		"""SCPI: IPM:RSTep:STEP:MAXimum \n
		Snippet: driver.ipm.rstep.step.set_maximum(maximum = 1.0) \n
		Sets the step size range. \n
			:param maximum: float Range: 0.1 to 0.5
		"""
		param = Conversions.decimal_value_to_str(maximum)
		self._core.io.write(f'IPM:RSTep:STEP:MAXimum {param}')

	def get_minimum(self) -> float:
		"""SCPI: IPM:RSTep:STEP:MINimum \n
		Snippet: value: float = driver.ipm.rstep.step.get_minimum() \n
		Sets the step size range. \n
			:return: minimum: No help available
		"""
		response = self._core.io.query_str('IPM:RSTep:STEP:MINimum?')
		return Conversions.str_to_float(response)

	def set_minimum(self, minimum: float) -> None:
		"""SCPI: IPM:RSTep:STEP:MINimum \n
		Snippet: driver.ipm.rstep.step.set_minimum(minimum = 1.0) \n
		Sets the step size range. \n
			:param minimum: float Range: 0.1 to 0.5
		"""
		param = Conversions.decimal_value_to_str(minimum)
		self._core.io.write(f'IPM:RSTep:STEP:MINimum {param}')
