from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Pmod:
	"""Pmod commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pmod", core, parent)

	# noinspection PyTypeChecker
	def get_direction(self) -> enums.SourceInt:
		"""SCPI: SETup:PMOD:DIRection \n
		Snippet: value: enums.SourceInt = driver.setup.pmod.get_direction() \n
		No command help available \n
			:return: direction: No help available
		"""
		response = self._core.io.query_str('SETup:PMOD:DIRection?')
		return Conversions.str_to_scalar_enum(response, enums.SourceInt)

	def set_direction(self, direction: enums.SourceInt) -> None:
		"""SCPI: SETup:PMOD:DIRection \n
		Snippet: driver.setup.pmod.set_direction(direction = enums.SourceInt.EXTernal) \n
		No command help available \n
			:param direction: No help available
		"""
		param = Conversions.enum_scalar_to_str(direction, enums.SourceInt)
		self._core.io.write(f'SETup:PMOD:DIRection {param}')

	def get_enable(self) -> bool:
		"""SCPI: SETup:PMOD:ENABle \n
		Snippet: value: bool = driver.setup.pmod.get_enable() \n
		Enables the activation of the pulse modulator for improving the on/off ratio. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SETup:PMOD:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SETup:PMOD:ENABle \n
		Snippet: driver.setup.pmod.set_enable(enable = False) \n
		Enables the activation of the pulse modulator for improving the on/off ratio. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SETup:PMOD:ENABle {param}')
