from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HigHq:
	"""HigHq commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("higHq", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: SETup:HIGHq:ENABle \n
		Snippet: value: bool = driver.setup.higHq.get_enable() \n
		Sets the I/Q modulator of signal generator to work in a high quality mode. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SETup:HIGHq:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SETup:HIGHq:ENABle \n
		Snippet: driver.setup.higHq.set_enable(enable = False) \n
		Sets the I/Q modulator of signal generator to work in a high quality mode. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SETup:HIGHq:ENABle {param}')

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.HqMode:
		"""SCPI: SETup:HIGHq:MODE \n
		Snippet: value: enums.HqMode = driver.setup.higHq.get_mode() \n
		Defines which high-quality mode is used. Requires that method RsPulseSeq.Setup.HigHq.enable is set to ON (see method
		RsPulseSeq.Setup.HigHq.enable) . \n
			:return: mode: NORMal| TABLe NORM Enables compensation for I/Q skew and frequency response correction. This mode generates a flat signal over a large bandwidth but requires longer setting time and can lead to signal interruption. TABL This mode provides optimization while maintaining settling time.
		"""
		response = self._core.io.query_str('SETup:HIGHq:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.HqMode)

	def set_mode(self, mode: enums.HqMode) -> None:
		"""SCPI: SETup:HIGHq:MODE \n
		Snippet: driver.setup.higHq.set_mode(mode = enums.HqMode.NORMal) \n
		Defines which high-quality mode is used. Requires that method RsPulseSeq.Setup.HigHq.enable is set to ON (see method
		RsPulseSeq.Setup.HigHq.enable) . \n
			:param mode: NORMal| TABLe NORM Enables compensation for I/Q skew and frequency response correction. This mode generates a flat signal over a large bandwidth but requires longer setting time and can lead to signal interruption. TABL This mode provides optimization while maintaining settling time.
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.HqMode)
		self._core.io.write(f'SETup:HIGHq:MODE {param}')
