from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Exclude:
	"""Exclude commands group definition. 6 total commands, 2 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("exclude", core, parent)

	@property
	def level(self):
		"""level commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_level'):
			from .Level import Level
			self._level = Level(self._core, self._cmd_group)
		return self._level

	@property
	def time(self):
		"""time commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_time'):
			from .Time import Time
			self._time = Time(self._core, self._cmd_group)
		return self._time

	def get_enable(self) -> bool:
		"""SCPI: PULSe:MOP:EXCLude:ENABle \n
		Snippet: value: bool = driver.pulse.mop.exclude.get_enable() \n
		Activates the restriction of the modulation. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PULSe:MOP:EXCLude:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: PULSe:MOP:EXCLude:ENABle \n
		Snippet: driver.pulse.mop.exclude.set_enable(enable = False) \n
		Activates the restriction of the modulation. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'PULSe:MOP:EXCLude:ENABle {param}')

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.ExcMode:
		"""SCPI: PULSe:MOP:EXCLude:MODE \n
		Snippet: value: enums.ExcMode = driver.pulse.mop.exclude.get_mode() \n
		Selects the parameter that determines the area on that the MOP is applied. \n
			:return: mode: TIME| LEVel| WIDTh
		"""
		response = self._core.io.query_str('PULSe:MOP:EXCLude:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.ExcMode)

	def set_mode(self, mode: enums.ExcMode) -> None:
		"""SCPI: PULSe:MOP:EXCLude:MODE \n
		Snippet: driver.pulse.mop.exclude.set_mode(mode = enums.ExcMode.LEVel) \n
		Selects the parameter that determines the area on that the MOP is applied. \n
			:param mode: TIME| LEVel| WIDTh
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.ExcMode)
		self._core.io.write(f'PULSe:MOP:EXCLude:MODE {param}')

	def clone(self) -> 'Exclude':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Exclude(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
