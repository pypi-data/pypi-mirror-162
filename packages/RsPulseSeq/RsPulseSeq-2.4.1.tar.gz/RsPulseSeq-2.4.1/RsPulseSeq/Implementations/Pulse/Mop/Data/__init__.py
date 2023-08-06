from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Data:
	"""Data commands group definition. 3 total commands, 1 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("data", core, parent)

	@property
	def dsrc(self):
		"""dsrc commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_dsrc'):
			from .Dsrc import Dsrc
			self._dsrc = Dsrc(self._core, self._cmd_group)
		return self._dsrc

	# noinspection PyTypeChecker
	def get_coding(self) -> enums.Coding:
		"""SCPI: PULSe:MOP:DATA:CODing \n
		Snippet: value: enums.Coding = driver.pulse.mop.data.get_coding() \n
		Selects the data coding scheme. \n
			:return: coding: NONE| DIFFerential| GRAY| DGRay
		"""
		response = self._core.io.query_str('PULSe:MOP:DATA:CODing?')
		return Conversions.str_to_scalar_enum(response, enums.Coding)

	def set_coding(self, coding: enums.Coding) -> None:
		"""SCPI: PULSe:MOP:DATA:CODing \n
		Snippet: driver.pulse.mop.data.set_coding(coding = enums.Coding.DGRay) \n
		Selects the data coding scheme. \n
			:param coding: NONE| DIFFerential| GRAY| DGRay
		"""
		param = Conversions.enum_scalar_to_str(coding, enums.Coding)
		self._core.io.write(f'PULSe:MOP:DATA:CODing {param}')

	def clone(self) -> 'Data':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Data(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
