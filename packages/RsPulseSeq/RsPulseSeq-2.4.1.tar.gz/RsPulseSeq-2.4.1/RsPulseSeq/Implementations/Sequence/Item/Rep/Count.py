from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Count:
	"""Count commands group definition. 5 total commands, 0 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	def get_duration(self) -> float:
		"""SCPI: SEQuence:ITEM:REP:COUNt:DURation \n
		Snippet: value: float = driver.sequence.item.rep.count.get_duration() \n
		Sets a time duration. \n
			:return: duration: float Range: 0 to 1e+09, Unit: sec
		"""
		response = self._core.io.query_str('SEQuence:ITEM:REP:COUNt:DURation?')
		return Conversions.str_to_float(response)

	def set_duration(self, duration: float) -> None:
		"""SCPI: SEQuence:ITEM:REP:COUNt:DURation \n
		Snippet: driver.sequence.item.rep.count.set_duration(duration = 1.0) \n
		Sets a time duration. \n
			:param duration: float Range: 0 to 1e+09, Unit: sec
		"""
		param = Conversions.decimal_value_to_str(duration)
		self._core.io.write(f'SEQuence:ITEM:REP:COUNt:DURation {param}')

	def get_fixed(self) -> float:
		"""SCPI: SEQuence:ITEM:REP:COUNt:FIXed \n
		Snippet: value: float = driver.sequence.item.rep.count.get_fixed() \n
		Sets the repetition number as a numeric value. \n
			:return: fixed: float Range: 1 to 65535
		"""
		response = self._core.io.query_str('SEQuence:ITEM:REP:COUNt:FIXed?')
		return Conversions.str_to_float(response)

	def set_fixed(self, fixed: float) -> None:
		"""SCPI: SEQuence:ITEM:REP:COUNt:FIXed \n
		Snippet: driver.sequence.item.rep.count.set_fixed(fixed = 1.0) \n
		Sets the repetition number as a numeric value. \n
			:param fixed: float Range: 1 to 65535
		"""
		param = Conversions.decimal_value_to_str(fixed)
		self._core.io.write(f'SEQuence:ITEM:REP:COUNt:FIXed {param}')

	def get_maximum(self) -> float:
		"""SCPI: SEQuence:ITEM:REP:COUNt:MAXimum \n
		Snippet: value: float = driver.sequence.item.rep.count.get_maximum() \n
		Sets the value range of the repetition count. \n
			:return: maximum: float Range: 1 to 65535
		"""
		response = self._core.io.query_str('SEQuence:ITEM:REP:COUNt:MAXimum?')
		return Conversions.str_to_float(response)

	def set_maximum(self, maximum: float) -> None:
		"""SCPI: SEQuence:ITEM:REP:COUNt:MAXimum \n
		Snippet: driver.sequence.item.rep.count.set_maximum(maximum = 1.0) \n
		Sets the value range of the repetition count. \n
			:param maximum: float Range: 1 to 65535
		"""
		param = Conversions.decimal_value_to_str(maximum)
		self._core.io.write(f'SEQuence:ITEM:REP:COUNt:MAXimum {param}')

	def get_minimum(self) -> float:
		"""SCPI: SEQuence:ITEM:REP:COUNt:MINimum \n
		Snippet: value: float = driver.sequence.item.rep.count.get_minimum() \n
		Sets the value range of the repetition count. \n
			:return: minimum: No help available
		"""
		response = self._core.io.query_str('SEQuence:ITEM:REP:COUNt:MINimum?')
		return Conversions.str_to_float(response)

	def set_minimum(self, minimum: float) -> None:
		"""SCPI: SEQuence:ITEM:REP:COUNt:MINimum \n
		Snippet: driver.sequence.item.rep.count.set_minimum(minimum = 1.0) \n
		Sets the value range of the repetition count. \n
			:param minimum: float Range: 1 to 65535
		"""
		param = Conversions.decimal_value_to_str(minimum)
		self._core.io.write(f'SEQuence:ITEM:REP:COUNt:MINimum {param}')

	def get_step(self) -> float:
		"""SCPI: SEQuence:ITEM:REP:COUNt:STEP \n
		Snippet: value: float = driver.sequence.item.rep.count.get_step() \n
		Sets the repetition count granularity. \n
			:return: step: float Range: 1 to 65535
		"""
		response = self._core.io.query_str('SEQuence:ITEM:REP:COUNt:STEP?')
		return Conversions.str_to_float(response)

	def set_step(self, step: float) -> None:
		"""SCPI: SEQuence:ITEM:REP:COUNt:STEP \n
		Snippet: driver.sequence.item.rep.count.set_step(step = 1.0) \n
		Sets the repetition count granularity. \n
			:param step: float Range: 1 to 65535
		"""
		param = Conversions.decimal_value_to_str(step)
		self._core.io.write(f'SEQuence:ITEM:REP:COUNt:STEP {param}')
