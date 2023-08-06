from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Quesation:
	"""Quesation commands group definition. 5 total commands, 0 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("quesation", core, parent)

	def get_condition(self) -> float:
		"""SCPI: STATus:QUESation:CONDition \n
		Snippet: value: float = driver.status.quesation.get_condition() \n
		No command help available \n
			:return: condition: No help available
		"""
		response = self._core.io.query_str('STATus:QUESation:CONDition?')
		return Conversions.str_to_float(response)

	def get_enable(self) -> bool:
		"""SCPI: STATus:QUESation:ENABle \n
		Snippet: value: bool = driver.status.quesation.get_enable() \n
		No command help available \n
			:return: enable: No help available
		"""
		response = self._core.io.query_str('STATus:QUESation:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: STATus:QUESation:ENABle \n
		Snippet: driver.status.quesation.set_enable(enable = False) \n
		No command help available \n
			:param enable: No help available
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'STATus:QUESation:ENABle {param}')

	def get_event(self) -> float:
		"""SCPI: STATus:QUESation:EVENt \n
		Snippet: value: float = driver.status.quesation.get_event() \n
		No command help available \n
			:return: event: No help available
		"""
		response = self._core.io.query_str('STATus:QUESation:EVENt?')
		return Conversions.str_to_float(response)

	def get_ntransition(self) -> float:
		"""SCPI: STATus:QUESation:NTRansition \n
		Snippet: value: float = driver.status.quesation.get_ntransition() \n
		No command help available \n
			:return: ntransition: No help available
		"""
		response = self._core.io.query_str('STATus:QUESation:NTRansition?')
		return Conversions.str_to_float(response)

	def set_ntransition(self, ntransition: float) -> None:
		"""SCPI: STATus:QUESation:NTRansition \n
		Snippet: driver.status.quesation.set_ntransition(ntransition = 1.0) \n
		No command help available \n
			:param ntransition: No help available
		"""
		param = Conversions.decimal_value_to_str(ntransition)
		self._core.io.write(f'STATus:QUESation:NTRansition {param}')

	def get_ptransition(self) -> float:
		"""SCPI: STATus:QUESation:PTRansition \n
		Snippet: value: float = driver.status.quesation.get_ptransition() \n
		No command help available \n
			:return: ptransition: No help available
		"""
		response = self._core.io.query_str('STATus:QUESation:PTRansition?')
		return Conversions.str_to_float(response)

	def set_ptransition(self, ptransition: float) -> None:
		"""SCPI: STATus:QUESation:PTRansition \n
		Snippet: driver.status.quesation.set_ptransition(ptransition = 1.0) \n
		No command help available \n
			:param ptransition: No help available
		"""
		param = Conversions.decimal_value_to_str(ptransition)
		self._core.io.write(f'STATus:QUESation:PTRansition {param}')
