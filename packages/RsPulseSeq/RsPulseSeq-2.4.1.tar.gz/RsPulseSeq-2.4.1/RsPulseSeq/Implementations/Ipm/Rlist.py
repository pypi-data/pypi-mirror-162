from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Rlist:
	"""Rlist commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rlist", core, parent)

	# noinspection PyTypeChecker
	def get_base(self) -> enums.BaseDomainB:
		"""SCPI: IPM:RLISt:BASE \n
		Snippet: value: enums.BaseDomainB = driver.ipm.rlist.get_base() \n
		Sets the IPM profile base and defines how the increments repetition is defined. \n
			:return: base: LENGth| TIME LENGth Increments are repeated several times, as set with the command method RsPulseSeq.Ipm.Rlist.burst. TIME Increments are repeated for the defined time duration, as set with the command method RsPulseSeq.Ipm.Rlist.period.
		"""
		response = self._core.io.query_str('IPM:RLISt:BASE?')
		return Conversions.str_to_scalar_enum(response, enums.BaseDomainB)

	def set_base(self, base: enums.BaseDomainB) -> None:
		"""SCPI: IPM:RLISt:BASE \n
		Snippet: driver.ipm.rlist.set_base(base = enums.BaseDomainB.LENGth) \n
		Sets the IPM profile base and defines how the increments repetition is defined. \n
			:param base: LENGth| TIME LENGth Increments are repeated several times, as set with the command method RsPulseSeq.Ipm.Rlist.burst. TIME Increments are repeated for the defined time duration, as set with the command method RsPulseSeq.Ipm.Rlist.period.
		"""
		param = Conversions.enum_scalar_to_str(base, enums.BaseDomainB)
		self._core.io.write(f'IPM:RLISt:BASE {param}')

	def get_burst(self) -> float:
		"""SCPI: IPM:RLISt:BURSt \n
		Snippet: value: float = driver.ipm.rlist.get_burst() \n
		Defines how many times an increment is repeated. \n
			:return: burst: float Range: 1 to 8192
		"""
		response = self._core.io.query_str('IPM:RLISt:BURSt?')
		return Conversions.str_to_float(response)

	def set_burst(self, burst: float) -> None:
		"""SCPI: IPM:RLISt:BURSt \n
		Snippet: driver.ipm.rlist.set_burst(burst = 1.0) \n
		Defines how many times an increment is repeated. \n
			:param burst: float Range: 1 to 8192
		"""
		param = Conversions.decimal_value_to_str(burst)
		self._core.io.write(f'IPM:RLISt:BURSt {param}')

	def get_period(self) -> float:
		"""SCPI: IPM:RLISt:PERiod \n
		Snippet: value: float = driver.ipm.rlist.get_period() \n
		Sets how long an increment is repeated. \n
			:return: period: float Range: 1e-09 to 1e+09
		"""
		response = self._core.io.query_str('IPM:RLISt:PERiod?')
		return Conversions.str_to_float(response)

	def set_period(self, period: float) -> None:
		"""SCPI: IPM:RLISt:PERiod \n
		Snippet: driver.ipm.rlist.set_period(period = 1.0) \n
		Sets how long an increment is repeated. \n
			:param period: float Range: 1e-09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(period)
		self._core.io.write(f'IPM:RLISt:PERiod {param}')

	def get_reuse(self) -> bool:
		"""SCPI: IPM:RLISt:REUSe \n
		Snippet: value: bool = driver.ipm.rlist.get_reuse() \n
		If disabled, each value is used only once. \n
			:return: reuse: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('IPM:RLISt:REUSe?')
		return Conversions.str_to_bool(response)

	def set_reuse(self, reuse: bool) -> None:
		"""SCPI: IPM:RLISt:REUSe \n
		Snippet: driver.ipm.rlist.set_reuse(reuse = False) \n
		If disabled, each value is used only once. \n
			:param reuse: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(reuse)
		self._core.io.write(f'IPM:RLISt:REUSe {param}')
