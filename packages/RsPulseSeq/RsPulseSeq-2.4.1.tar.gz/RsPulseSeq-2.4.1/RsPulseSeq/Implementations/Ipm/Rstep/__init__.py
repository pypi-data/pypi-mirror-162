from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Rstep:
	"""Rstep commands group definition. 5 total commands, 1 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rstep", core, parent)

	@property
	def step(self):
		"""step commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_step'):
			from .Step import Step
			self._step = Step(self._core, self._cmd_group)
		return self._step

	def get_maximum(self) -> float:
		"""SCPI: IPM:RSTep:MAXimum \n
		Snippet: value: float = driver.ipm.rstep.get_maximum() \n
		Sets the value range. \n
			:return: maximum: float Range: 0 to 1e+11
		"""
		response = self._core.io.query_str('IPM:RSTep:MAXimum?')
		return Conversions.str_to_float(response)

	def set_maximum(self, maximum: float) -> None:
		"""SCPI: IPM:RSTep:MAXimum \n
		Snippet: driver.ipm.rstep.set_maximum(maximum = 1.0) \n
		Sets the value range. \n
			:param maximum: float Range: 0 to 1e+11
		"""
		param = Conversions.decimal_value_to_str(maximum)
		self._core.io.write(f'IPM:RSTep:MAXimum {param}')

	def get_minimum(self) -> float:
		"""SCPI: IPM:RSTep:MINimum \n
		Snippet: value: float = driver.ipm.rstep.get_minimum() \n
		Sets the value range. \n
			:return: minimum: No help available
		"""
		response = self._core.io.query_str('IPM:RSTep:MINimum?')
		return Conversions.str_to_float(response)

	def set_minimum(self, minimum: float) -> None:
		"""SCPI: IPM:RSTep:MINimum \n
		Snippet: driver.ipm.rstep.set_minimum(minimum = 1.0) \n
		Sets the value range. \n
			:param minimum: float Range: 0 to 1e+11
		"""
		param = Conversions.decimal_value_to_str(minimum)
		self._core.io.write(f'IPM:RSTep:MINimum {param}')

	def get_period(self) -> float:
		"""SCPI: IPM:RSTep:PERiod \n
		Snippet: value: float = driver.ipm.rstep.get_period() \n
		Sets the pattern length. \n
			:return: period: float Range: 0 to 4096
		"""
		response = self._core.io.query_str('IPM:RSTep:PERiod?')
		return Conversions.str_to_float(response)

	def set_period(self, period: float) -> None:
		"""SCPI: IPM:RSTep:PERiod \n
		Snippet: driver.ipm.rstep.set_period(period = 1.0) \n
		Sets the pattern length. \n
			:param period: float Range: 0 to 4096
		"""
		param = Conversions.decimal_value_to_str(period)
		self._core.io.write(f'IPM:RSTep:PERiod {param}')

	def clone(self) -> 'Rstep':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Rstep(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
