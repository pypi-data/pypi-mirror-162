from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Phase:
	"""Phase commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("phase", core, parent)

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.PhaseMode:
		"""SCPI: SEQuence:PHASe:MODE \n
		Snippet: value: enums.PhaseMode = driver.sequence.phase.get_mode() \n
		Defines how the phase is set at each pulse start. \n
			:return: mode: ABSolute| CONTinuous| MEMory
		"""
		response = self._core.io.query_str('SEQuence:PHASe:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.PhaseMode)

	def set_mode(self, mode: enums.PhaseMode) -> None:
		"""SCPI: SEQuence:PHASe:MODE \n
		Snippet: driver.sequence.phase.set_mode(mode = enums.PhaseMode.ABSolute) \n
		Defines how the phase is set at each pulse start. \n
			:param mode: ABSolute| CONTinuous| MEMory
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.PhaseMode)
		self._core.io.write(f'SEQuence:PHASe:MODE {param}')
