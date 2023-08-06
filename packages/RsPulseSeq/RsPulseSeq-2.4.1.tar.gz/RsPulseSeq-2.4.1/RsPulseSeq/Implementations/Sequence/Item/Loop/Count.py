from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Count:
	"""Count commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	def get_fixed(self) -> float:
		"""SCPI: SEQuence:ITEM:LOOP:COUNt:FIXed \n
		Snippet: value: float = driver.sequence.item.loop.count.get_fixed() \n
		Sets the repetition number as a numeric value. \n
			:return: fixed: float Range: 1 to 65535
		"""
		response = self._core.io.query_str('SEQuence:ITEM:LOOP:COUNt:FIXed?')
		return Conversions.str_to_float(response)

	def set_fixed(self, fixed: float) -> None:
		"""SCPI: SEQuence:ITEM:LOOP:COUNt:FIXed \n
		Snippet: driver.sequence.item.loop.count.set_fixed(fixed = 1.0) \n
		Sets the repetition number as a numeric value. \n
			:param fixed: float Range: 1 to 65535
		"""
		param = Conversions.decimal_value_to_str(fixed)
		self._core.io.write(f'SEQuence:ITEM:LOOP:COUNt:FIXed {param}')

	def get_maximum(self) -> float:
		"""SCPI: SEQuence:ITEM:LOOP:COUNt:MAXimum \n
		Snippet: value: float = driver.sequence.item.loop.count.get_maximum() \n
		Sets the value range of the loop count. \n
			:return: maximum: float Range: 1 to 65535
		"""
		response = self._core.io.query_str('SEQuence:ITEM:LOOP:COUNt:MAXimum?')
		return Conversions.str_to_float(response)

	def set_maximum(self, maximum: float) -> None:
		"""SCPI: SEQuence:ITEM:LOOP:COUNt:MAXimum \n
		Snippet: driver.sequence.item.loop.count.set_maximum(maximum = 1.0) \n
		Sets the value range of the loop count. \n
			:param maximum: float Range: 1 to 65535
		"""
		param = Conversions.decimal_value_to_str(maximum)
		self._core.io.write(f'SEQuence:ITEM:LOOP:COUNt:MAXimum {param}')

	def get_minimum(self) -> float:
		"""SCPI: SEQuence:ITEM:LOOP:COUNt:MINimum \n
		Snippet: value: float = driver.sequence.item.loop.count.get_minimum() \n
		Sets the value range of the loop count. \n
			:return: minimum: No help available
		"""
		response = self._core.io.query_str('SEQuence:ITEM:LOOP:COUNt:MINimum?')
		return Conversions.str_to_float(response)

	def set_minimum(self, minimum: float) -> None:
		"""SCPI: SEQuence:ITEM:LOOP:COUNt:MINimum \n
		Snippet: driver.sequence.item.loop.count.set_minimum(minimum = 1.0) \n
		Sets the value range of the loop count. \n
			:param minimum: float Range: 1 to 65535
		"""
		param = Conversions.decimal_value_to_str(minimum)
		self._core.io.write(f'SEQuence:ITEM:LOOP:COUNt:MINimum {param}')

	def get_step(self) -> float:
		"""SCPI: SEQuence:ITEM:LOOP:COUNt:STEP \n
		Snippet: value: float = driver.sequence.item.loop.count.get_step() \n
		Sets the loop count granularity. \n
			:return: step: float Range: 1 to 65535
		"""
		response = self._core.io.query_str('SEQuence:ITEM:LOOP:COUNt:STEP?')
		return Conversions.str_to_float(response)

	def set_step(self, step: float) -> None:
		"""SCPI: SEQuence:ITEM:LOOP:COUNt:STEP \n
		Snippet: driver.sequence.item.loop.count.set_step(step = 1.0) \n
		Sets the loop count granularity. \n
			:param step: float Range: 1 to 65535
		"""
		param = Conversions.decimal_value_to_str(step)
		self._core.io.write(f'SEQuence:ITEM:LOOP:COUNt:STEP {param}')
