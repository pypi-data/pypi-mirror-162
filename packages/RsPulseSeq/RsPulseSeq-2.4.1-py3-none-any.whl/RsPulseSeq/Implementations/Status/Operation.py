from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Operation:
	"""Operation commands group definition. 5 total commands, 0 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("operation", core, parent)

	def get_condition(self) -> float:
		"""SCPI: STATus:OPERation:CONDition \n
		Snippet: value: float = driver.status.operation.get_condition() \n
		Queries the content of the CONDition part of the STATus:OPERation register. This part contains information on the action
		currently being performed in the instrument. The content is not deleted after being read out because it indicates the
		current status. \n
			:return: condition: float
		"""
		response = self._core.io.query_str('STATus:OPERation:CONDition?')
		return Conversions.str_to_float(response)

	def get_enable(self) -> bool:
		"""SCPI: STATus:OPERation:ENABle \n
		Snippet: value: bool = driver.status.operation.get_enable() \n
		No command help available \n
			:return: enable: No help available
		"""
		response = self._core.io.query_str('STATus:OPERation:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: STATus:OPERation:ENABle \n
		Snippet: driver.status.operation.set_enable(enable = False) \n
		No command help available \n
			:param enable: No help available
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'STATus:OPERation:ENABle {param}')

	def get_event(self) -> float:
		"""SCPI: STATus:OPERation:EVENt \n
		Snippet: value: float = driver.status.operation.get_event() \n
		No command help available \n
			:return: event: No help available
		"""
		response = self._core.io.query_str('STATus:OPERation:EVENt?')
		return Conversions.str_to_float(response)

	def get_ntransition(self) -> float:
		"""SCPI: STATus:OPERation:NTRansition \n
		Snippet: value: float = driver.status.operation.get_ntransition() \n
		No command help available \n
			:return: ntransition: No help available
		"""
		response = self._core.io.query_str('STATus:OPERation:NTRansition?')
		return Conversions.str_to_float(response)

	def set_ntransition(self, ntransition: float) -> None:
		"""SCPI: STATus:OPERation:NTRansition \n
		Snippet: driver.status.operation.set_ntransition(ntransition = 1.0) \n
		No command help available \n
			:param ntransition: No help available
		"""
		param = Conversions.decimal_value_to_str(ntransition)
		self._core.io.write(f'STATus:OPERation:NTRansition {param}')

	def get_ptransition(self) -> float:
		"""SCPI: STATus:OPERation:PTRansition \n
		Snippet: value: float = driver.status.operation.get_ptransition() \n
		No command help available \n
			:return: ptransition: No help available
		"""
		response = self._core.io.query_str('STATus:OPERation:PTRansition?')
		return Conversions.str_to_float(response)

	def set_ptransition(self, ptransition: float) -> None:
		"""SCPI: STATus:OPERation:PTRansition \n
		Snippet: driver.status.operation.set_ptransition(ptransition = 1.0) \n
		No command help available \n
			:param ptransition: No help available
		"""
		param = Conversions.decimal_value_to_str(ptransition)
		self._core.io.write(f'STATus:OPERation:PTRansition {param}')
