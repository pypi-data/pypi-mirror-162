from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ......Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Antenna:
	"""Antenna commands group definition. 5 total commands, 1 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("antenna", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	def clear(self) -> None:
		"""SCPI: ASSignment:DESTination:PATH:ANTenna:CLEar \n
		Snippet: driver.assignment.destination.path.antenna.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'ASSignment:DESTination:PATH:ANTenna:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: ASSignment:DESTination:PATH:ANTenna:CLEar \n
		Snippet: driver.assignment.destination.path.antenna.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'ASSignment:DESTination:PATH:ANTenna:CLEar', opc_timeout_ms)

	def delete(self) -> None:
		"""SCPI: ASSignment:DESTination:PATH:ANTenna:DELete \n
		Snippet: driver.assignment.destination.path.antenna.delete() \n
		Deletes the particular item. \n
		"""
		self._core.io.write(f'ASSignment:DESTination:PATH:ANTenna:DELete')

	def delete_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: ASSignment:DESTination:PATH:ANTenna:DELete \n
		Snippet: driver.assignment.destination.path.antenna.delete_with_opc() \n
		Deletes the particular item. \n
		Same as delete, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'ASSignment:DESTination:PATH:ANTenna:DELete', opc_timeout_ms)

	def get_list_py(self) -> str:
		"""SCPI: ASSignment:DESTination:PATH:ANTenna:LIST \n
		Snippet: value: str = driver.assignment.destination.path.antenna.get_list_py() \n
		Queries the list of assigned receiver signals to the selected plugin. \n
			:return: list_py: 'ReceiverSignal#1','ReceiverSignal#2',...
		"""
		response = self._core.io.query_str('ASSignment:DESTination:PATH:ANTenna:LIST?')
		return trim_str_response(response)

	def get_select(self) -> str:
		"""SCPI: ASSignment:DESTination:PATH:ANTenna:SELect \n
		Snippet: value: str = driver.assignment.destination.path.antenna.get_select() \n
		Selects the element to which the subsequent commands apply. \n
			:return: select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Destination.Path.Antenna.listPy
		"""
		response = self._core.io.query_str('ASSignment:DESTination:PATH:ANTenna:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: ASSignment:DESTination:PATH:ANTenna:SELect \n
		Snippet: driver.assignment.destination.path.antenna.set_select(select = '1') \n
		Selects the element to which the subsequent commands apply. \n
			:param select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Destination.Path.Antenna.listPy
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'ASSignment:DESTination:PATH:ANTenna:SELect {param}')

	def clone(self) -> 'Antenna':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Antenna(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
