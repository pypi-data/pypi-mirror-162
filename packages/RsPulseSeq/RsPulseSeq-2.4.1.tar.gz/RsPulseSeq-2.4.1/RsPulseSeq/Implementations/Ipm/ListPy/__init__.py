from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ListPy:
	"""ListPy commands group definition. 13 total commands, 2 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("listPy", core, parent)

	@property
	def firing(self):
		"""firing commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_firing'):
			from .Firing import Firing
			self._firing = Firing(self._core, self._cmd_group)
		return self._firing

	@property
	def item(self):
		"""item commands group. 1 Sub-classes, 6 commands."""
		if not hasattr(self, '_item'):
			from .Item import Item
			self._item = Item(self._core, self._cmd_group)
		return self._item

	# noinspection PyTypeChecker
	def get_base(self) -> enums.BaseDomain:
		"""SCPI: IPM:LIST:BASE \n
		Snippet: value: enums.BaseDomain = driver.ipm.listPy.get_base() \n
		Sets the IPM profile base and defines how the steps repetition is defined. \n
			:return: base: PULSe| TIME PULSe Steps are repeated several times, as set with the command method RsPulseSeq.Ipm.ListPy.Item.repetition. TIME Steps are repeated for the defined time duration, as set with the command method RsPulseSeq.Ipm.ListPy.Item.time.
		"""
		response = self._core.io.query_str('IPM:LIST:BASE?')
		return Conversions.str_to_scalar_enum(response, enums.BaseDomain)

	def set_base(self, base: enums.BaseDomain) -> None:
		"""SCPI: IPM:LIST:BASE \n
		Snippet: driver.ipm.listPy.set_base(base = enums.BaseDomain.PULSe) \n
		Sets the IPM profile base and defines how the steps repetition is defined. \n
			:param base: PULSe| TIME PULSe Steps are repeated several times, as set with the command method RsPulseSeq.Ipm.ListPy.Item.repetition. TIME Steps are repeated for the defined time duration, as set with the command method RsPulseSeq.Ipm.ListPy.Item.time.
		"""
		param = Conversions.enum_scalar_to_str(base, enums.BaseDomain)
		self._core.io.write(f'IPM:LIST:BASE {param}')

	def clear(self) -> None:
		"""SCPI: IPM:LIST:CLEar \n
		Snippet: driver.ipm.listPy.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'IPM:LIST:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: IPM:LIST:CLEar \n
		Snippet: driver.ipm.listPy.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'IPM:LIST:CLEar', opc_timeout_ms)

	def get_load(self) -> str:
		"""SCPI: IPM:LIST:LOAD \n
		Snippet: value: str = driver.ipm.listPy.get_load() \n
		Loads an IPM profile form an ASCII file. \n
			:return: load: string File path, file name, and file extension
		"""
		response = self._core.io.query_str('IPM:LIST:LOAD?')
		return trim_str_response(response)

	def set_load(self, load: str) -> None:
		"""SCPI: IPM:LIST:LOAD \n
		Snippet: driver.ipm.listPy.set_load(load = '1') \n
		Loads an IPM profile form an ASCII file. \n
			:param load: string File path, file name, and file extension
		"""
		param = Conversions.value_to_quoted_str(load)
		self._core.io.write(f'IPM:LIST:LOAD {param}')

	def get_save(self) -> str:
		"""SCPI: IPM:LIST:SAVE \n
		Snippet: value: str = driver.ipm.listPy.get_save() \n
		Stores the IPM profile as a file. \n
			:return: save: string File path incl. file name and extension.
		"""
		response = self._core.io.query_str('IPM:LIST:SAVE?')
		return trim_str_response(response)

	def set_save(self, save: str) -> None:
		"""SCPI: IPM:LIST:SAVE \n
		Snippet: driver.ipm.listPy.set_save(save = '1') \n
		Stores the IPM profile as a file. \n
			:param save: string File path incl. file name and extension.
		"""
		param = Conversions.value_to_quoted_str(save)
		self._core.io.write(f'IPM:LIST:SAVE {param}')

	def clone(self) -> 'ListPy':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ListPy(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
