from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ......Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Variable:
	"""Variable commands group definition. 5 total commands, 1 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("variable", core, parent)

	@property
	def select(self):
		"""select commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_select'):
			from .Select import Select
			self._select = Select(self._core, self._cmd_group)
		return self._select

	def get_catalog(self) -> str:
		"""SCPI: SCENario:PDW:PLUGin:VARiable:CATalog \n
		Snippet: value: str = driver.scenario.pdw.plugin.variable.get_catalog() \n
		Queries the variables used in the plugin. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('SCENario:PDW:PLUGin:VARiable:CATalog?')
		return trim_str_response(response)

	def reset(self) -> None:
		"""SCPI: SCENario:PDW:PLUGin:VARiable:RESet \n
		Snippet: driver.scenario.pdw.plugin.variable.reset() \n
		Resets the variable values to the defaults. \n
		"""
		self._core.io.write(f'SCENario:PDW:PLUGin:VARiable:RESet')

	def reset_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:PDW:PLUGin:VARiable:RESet \n
		Snippet: driver.scenario.pdw.plugin.variable.reset_with_opc() \n
		Resets the variable values to the defaults. \n
		Same as reset, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:PDW:PLUGin:VARiable:RESet', opc_timeout_ms)

	def get_value(self) -> str:
		"""SCPI: SCENario:PDW:PLUGin:VARiable:VALue \n
		Snippet: value: str = driver.scenario.pdw.plugin.variable.get_value() \n
		Sets the values of the selected variable. \n
			:return: value: string
		"""
		response = self._core.io.query_str('SCENario:PDW:PLUGin:VARiable:VALue?')
		return trim_str_response(response)

	def set_value(self, value: str) -> None:
		"""SCPI: SCENario:PDW:PLUGin:VARiable:VALue \n
		Snippet: driver.scenario.pdw.plugin.variable.set_value(value = '1') \n
		Sets the values of the selected variable. \n
			:param value: string
		"""
		param = Conversions.value_to_quoted_str(value)
		self._core.io.write(f'SCENario:PDW:PLUGin:VARiable:VALue {param}')

	def clone(self) -> 'Variable':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Variable(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
