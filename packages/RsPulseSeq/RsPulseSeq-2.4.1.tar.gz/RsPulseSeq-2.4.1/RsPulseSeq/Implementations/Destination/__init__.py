from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Destination:
	"""Destination commands group definition. 12 total commands, 1 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("destination", core, parent)

	@property
	def plugin(self):
		"""plugin commands group. 1 Sub-classes, 1 commands."""
		if not hasattr(self, '_plugin'):
			from .Plugin import Plugin
			self._plugin = Plugin(self._core, self._cmd_group)
		return self._plugin

	def set_add(self, add: str) -> None:
		"""SCPI: DESTination:ADD \n
		Snippet: driver.destination.set_add(add = '1') \n
		Adds a destination to the list. \n
			:param add: string
		"""
		param = Conversions.value_to_quoted_str(add)
		self._core.io.write(f'DESTination:ADD {param}')

	def clear(self) -> None:
		"""SCPI: DESTination:CLEar \n
		Snippet: driver.destination.clear() \n
		Deletes all destinations from the current list. \n
		"""
		self._core.io.write(f'DESTination:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: DESTination:CLEar \n
		Snippet: driver.destination.clear_with_opc() \n
		Deletes all destinations from the current list. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'DESTination:CLEar', opc_timeout_ms)

	def get_count(self) -> float:
		"""SCPI: DESTination:COUNt \n
		Snippet: value: float = driver.destination.get_count() \n
		Queries the number of available destinations. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('DESTination:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: DESTination:DELete \n
		Snippet: driver.destination.delete(delete = 1.0) \n
		Deletes the selected destination from the list. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'DESTination:DELete {param}')

	def get_name(self) -> str:
		"""SCPI: DESTination:NAME \n
		Snippet: value: str = driver.destination.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('DESTination:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: DESTination:NAME \n
		Snippet: driver.destination.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'DESTination:NAME {param}')

	def get_select(self) -> float:
		"""SCPI: DESTination:SELect \n
		Snippet: value: float = driver.destination.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('DESTination:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: DESTination:SELect \n
		Snippet: driver.destination.set_select(select = 1.0) \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'DESTination:SELect {param}')

	def clone(self) -> 'Destination':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Destination(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
