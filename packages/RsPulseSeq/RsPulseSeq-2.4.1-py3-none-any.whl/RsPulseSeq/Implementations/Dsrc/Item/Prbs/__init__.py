from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Prbs:
	"""Prbs commands group definition. 3 total commands, 1 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("prbs", core, parent)

	@property
	def init(self):
		"""init commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_init'):
			from .Init import Init
			self._init = Init(self._core, self._cmd_group)
		return self._init

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.PrbsType:
		"""SCPI: DSRC:ITEM:PRBS:TYPE \n
		Snippet: value: enums.PrbsType = driver.dsrc.item.prbs.get_type_py() \n
		Sets the PRBS type for the selected item. \n
			:return: type_py: P9| P11| P15| P16| P20| P21| P23| P7
		"""
		response = self._core.io.query_str('DSRC:ITEM:PRBS:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.PrbsType)

	def set_type_py(self, type_py: enums.PrbsType) -> None:
		"""SCPI: DSRC:ITEM:PRBS:TYPE \n
		Snippet: driver.dsrc.item.prbs.set_type_py(type_py = enums.PrbsType.P11) \n
		Sets the PRBS type for the selected item. \n
			:param type_py: P9| P11| P15| P16| P20| P21| P23| P7
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.PrbsType)
		self._core.io.write(f'DSRC:ITEM:PRBS:TYPE {param}')

	def clone(self) -> 'Prbs':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Prbs(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
