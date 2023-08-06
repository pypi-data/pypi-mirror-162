from typing import List

from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Setup:
	"""Setup commands group definition. 16 total commands, 4 Subgroups, 8 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("setup", core, parent)

	@property
	def higHq(self):
		"""higHq commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_higHq'):
			from .HigHq import HigHq
			self._higHq = HigHq(self._core, self._cmd_group)
		return self._higHq

	@property
	def locpl(self):
		"""locpl commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_locpl'):
			from .Locpl import Locpl
			self._locpl = Locpl(self._core, self._cmd_group)
		return self._locpl

	@property
	def pmod(self):
		"""pmod commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_pmod'):
			from .Pmod import Pmod
			self._pmod = Pmod(self._core, self._cmd_group)
		return self._pmod

	@property
	def rfAlign(self):
		"""rfAlign commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_rfAlign'):
			from .RfAlign import RfAlign
			self._rfAlign = RfAlign(self._core, self._cmd_group)
		return self._rfAlign

	def set_add(self, add: str) -> None:
		"""SCPI: SETup:ADD \n
		Snippet: driver.setup.set_add(add = '1') \n
		Appends new item. \n
			:param add: No help available
		"""
		param = Conversions.value_to_quoted_str(add)
		self._core.io.write(f'SETup:ADD {param}')

	# noinspection PyTypeChecker
	def get_bb_sync(self) -> enums.BbSync:
		"""SCPI: SETup:BBSYnc \n
		Snippet: value: enums.BbSync = driver.setup.get_bb_sync() \n
		Sets if and which method the signal generator uses to synchronize the signals in the baseband domain.
		Relevant in multi-instrument setups where the signals of the different emitters are generated in different paths and
		different signal generators. \n
			:return: bb_sync: UNSYnc| TRIGger| CTRigger UNSYnc Unsynchronized baseband generators TRIGger Synchronized setup, where the instruments are connected in a primary/secondary chain. General-purpose trigger signal is used. CTRigger Synchronized primary/secondary setup, that uses a dedicated common trigger signal.
		"""
		response = self._core.io.query_str('SETup:BBSYnc?')
		return Conversions.str_to_scalar_enum(response, enums.BbSync)

	def set_bb_sync(self, bb_sync: enums.BbSync) -> None:
		"""SCPI: SETup:BBSYnc \n
		Snippet: driver.setup.set_bb_sync(bb_sync = enums.BbSync.CTRigger) \n
		Sets if and which method the signal generator uses to synchronize the signals in the baseband domain.
		Relevant in multi-instrument setups where the signals of the different emitters are generated in different paths and
		different signal generators. \n
			:param bb_sync: UNSYnc| TRIGger| CTRigger UNSYnc Unsynchronized baseband generators TRIGger Synchronized setup, where the instruments are connected in a primary/secondary chain. General-purpose trigger signal is used. CTRigger Synchronized primary/secondary setup, that uses a dedicated common trigger signal.
		"""
		param = Conversions.enum_scalar_to_str(bb_sync, enums.BbSync)
		self._core.io.write(f'SETup:BBSYnc {param}')

	def get_count(self) -> float:
		"""SCPI: SETup:COUNt \n
		Snippet: value: float = driver.setup.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('SETup:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: SETup:DELete \n
		Snippet: driver.setup.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'SETup:DELete {param}')

	def export(self, export: str) -> None:
		"""SCPI: SETup:EXPort \n
		Snippet: driver.setup.export(export = '1') \n
		Save current setup in a file. \n
			:param export: Complete path, incl filename and file extension *.ps_hwsetup
		"""
		param = Conversions.value_to_quoted_str(export)
		self._core.io.write(f'SETup:EXPort {param}')

	def set_import_py(self, import_py: str) -> None:
		"""SCPI: SETup:IMPort \n
		Snippet: driver.setup.set_import_py(import_py = '1') \n
		Loads the selected setup file. Imported setups are appended in the list of setups. \n
			:param import_py: Complete path, incl filename and file extension *.ps_hwsetup
		"""
		param = Conversions.value_to_quoted_str(import_py)
		self._core.io.write(f'SETup:IMPort {param}')

	def get_list_py(self) -> List[int]:
		"""SCPI: SETup:LIST \n
		Snippet: value: List[int] = driver.setup.get_list_py() \n
		Queries the name of the available hardware setups. \n
			:return: list_py: 'Setup#1','Setup#2',...
		"""
		response = self._core.io.query_bin_or_ascii_int_list('SETup:LIST?')
		return response

	def get_select(self) -> str:
		"""SCPI: SETup:SELect \n
		Snippet: value: str = driver.setup.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('SETup:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: SETup:SELect \n
		Snippet: driver.setup.set_select(select = '1') \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'SETup:SELect {param}')

	def clone(self) -> 'Setup':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Setup(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
