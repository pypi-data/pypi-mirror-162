from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Time:
	"""Time commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("time", core, parent)

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.TimeMode:
		"""SCPI: SEQuence:TIME:MODE \n
		Snippet: value: enums.TimeMode = driver.sequence.time.get_mode() \n
		Switches between time-based (PRI) and frequency-based (PRF) pulse repetition definition. \n
			:return: mode: PRI| PRF
		"""
		response = self._core.io.query_str('SEQuence:TIME:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.TimeMode)

	def set_mode(self, mode: enums.TimeMode) -> None:
		"""SCPI: SEQuence:TIME:MODE \n
		Snippet: driver.sequence.time.set_mode(mode = enums.TimeMode.PRF) \n
		Switches between time-based (PRI) and frequency-based (PRF) pulse repetition definition. \n
			:param mode: PRI| PRF
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.TimeMode)
		self._core.io.write(f'SEQuence:TIME:MODE {param}')
