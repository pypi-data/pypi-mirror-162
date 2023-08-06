from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Destination:
	"""Destination commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("destination", core, parent)

	def clear(self) -> None:
		"""SCPI: SCENario:DESTination:CLEar \n
		Snippet: driver.scenario.destination.clear() \n
		No command help available \n
		"""
		self._core.io.write(f'SCENario:DESTination:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:DESTination:CLEar \n
		Snippet: driver.scenario.destination.clear_with_opc() \n
		No command help available \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:DESTination:CLEar', opc_timeout_ms)

	def get_value(self) -> str:
		"""SCPI: SCENario:DESTination \n
		Snippet: value: str = driver.scenario.destination.get_value() \n
		Sets the destination for the signal. \n
			:return: destination: string Use the command method RsPulseSeq.Destination.Plugin.Variable.catalog to query a list of available export plugins.
		"""
		response = self._core.io.query_str('SCENario:DESTination?')
		return trim_str_response(response)

	def set_value(self, destination: str) -> None:
		"""SCPI: SCENario:DESTination \n
		Snippet: driver.scenario.destination.set_value(destination = '1') \n
		Sets the destination for the signal. \n
			:param destination: string Use the command method RsPulseSeq.Destination.Plugin.Variable.catalog to query a list of available export plugins.
		"""
		param = Conversions.value_to_quoted_str(destination)
		self._core.io.write(f'SCENario:DESTination {param}')
