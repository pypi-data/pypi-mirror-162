from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Step:
	"""Step commands group definition. 6 total commands, 0 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("step", core, parent)

	# noinspection PyTypeChecker
	def get_base(self) -> enums.BaseDomainB:
		"""SCPI: IPM:STEP:BASE \n
		Snippet: value: enums.BaseDomainB = driver.ipm.step.get_base() \n
		Sets the IPM profile base and defines how the increments repetition is defined. \n
			:return: base: LENGth| TIME LENGth Steps are repeated several times, as set with the command method RsPulseSeq.Ipm.Step.burst. TIME Steps are repeated for the defined time duration, as set with the command method RsPulseSeq.Ipm.Step.period.
		"""
		response = self._core.io.query_str('IPM:STEP:BASE?')
		return Conversions.str_to_scalar_enum(response, enums.BaseDomainB)

	def set_base(self, base: enums.BaseDomainB) -> None:
		"""SCPI: IPM:STEP:BASE \n
		Snippet: driver.ipm.step.set_base(base = enums.BaseDomainB.LENGth) \n
		Sets the IPM profile base and defines how the increments repetition is defined. \n
			:param base: LENGth| TIME LENGth Steps are repeated several times, as set with the command method RsPulseSeq.Ipm.Step.burst. TIME Steps are repeated for the defined time duration, as set with the command method RsPulseSeq.Ipm.Step.period.
		"""
		param = Conversions.enum_scalar_to_str(base, enums.BaseDomainB)
		self._core.io.write(f'IPM:STEP:BASE {param}')

	def get_burst(self) -> float:
		"""SCPI: IPM:STEP:BURSt \n
		Snippet: value: float = driver.ipm.step.get_burst() \n
		Sets the number of times an increment is repeated. \n
			:return: burst: float Range: 1 to 1000
		"""
		response = self._core.io.query_str('IPM:STEP:BURSt?')
		return Conversions.str_to_float(response)

	def set_burst(self, burst: float) -> None:
		"""SCPI: IPM:STEP:BURSt \n
		Snippet: driver.ipm.step.set_burst(burst = 1.0) \n
		Sets the number of times an increment is repeated. \n
			:param burst: float Range: 1 to 1000
		"""
		param = Conversions.decimal_value_to_str(burst)
		self._core.io.write(f'IPM:STEP:BURSt {param}')

	def get_increment(self) -> float:
		"""SCPI: IPM:STEP:INCRement \n
		Snippet: value: float = driver.ipm.step.get_increment() \n
		Sets the step size. \n
			:return: increment: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('IPM:STEP:INCRement?')
		return Conversions.str_to_float(response)

	def set_increment(self, increment: float) -> None:
		"""SCPI: IPM:STEP:INCRement \n
		Snippet: driver.ipm.step.set_increment(increment = 1.0) \n
		Sets the step size. \n
			:param increment: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(increment)
		self._core.io.write(f'IPM:STEP:INCRement {param}')

	def get_period(self) -> float:
		"""SCPI: IPM:STEP:PERiod \n
		Snippet: value: float = driver.ipm.step.get_period() \n
		Sets how long an increment is repeated. \n
			:return: period: float Range: 1e-09 to 1e+09
		"""
		response = self._core.io.query_str('IPM:STEP:PERiod?')
		return Conversions.str_to_float(response)

	def set_period(self, period: float) -> None:
		"""SCPI: IPM:STEP:PERiod \n
		Snippet: driver.ipm.step.set_period(period = 1.0) \n
		Sets how long an increment is repeated. \n
			:param period: float Range: 1e-09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(period)
		self._core.io.write(f'IPM:STEP:PERiod {param}')

	def get_start(self) -> float:
		"""SCPI: IPM:STEP:STARt \n
		Snippet: value: float = driver.ipm.step.get_start() \n
		Sets the start value. \n
			:return: start: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('IPM:STEP:STARt?')
		return Conversions.str_to_float(response)

	def set_start(self, start: float) -> None:
		"""SCPI: IPM:STEP:STARt \n
		Snippet: driver.ipm.step.set_start(start = 1.0) \n
		Sets the start value. \n
			:param start: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(start)
		self._core.io.write(f'IPM:STEP:STARt {param}')

	def get_steps(self) -> float:
		"""SCPI: IPM:STEP:STEPs \n
		Snippet: value: float = driver.ipm.step.get_steps() \n
		Sets the number of steps. \n
			:return: steps: float Range: 1 to 10000
		"""
		response = self._core.io.query_str('IPM:STEP:STEPs?')
		return Conversions.str_to_float(response)

	def set_steps(self, steps: float) -> None:
		"""SCPI: IPM:STEP:STEPs \n
		Snippet: driver.ipm.step.set_steps(steps = 1.0) \n
		Sets the number of steps. \n
			:param steps: float Range: 1 to 10000
		"""
		param = Conversions.decimal_value_to_str(steps)
		self._core.io.write(f'IPM:STEP:STEPs {param}')
