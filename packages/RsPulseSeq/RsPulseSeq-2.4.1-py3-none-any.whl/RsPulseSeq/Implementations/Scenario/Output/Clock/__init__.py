from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Clock:
	"""Clock commands group definition. 4 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("clock", core, parent)

	@property
	def auto(self):
		"""auto commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_auto'):
			from .Auto import Auto
			self._auto = Auto(self._core, self._cmd_group)
		return self._auto

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.AutoManualMode:
		"""SCPI: SCENario:OUTPut:CLOCk:MODE \n
		Snippet: value: enums.AutoManualMode = driver.scenario.output.clock.get_mode() \n
		Sets the clock mode. \n
			:return: mode: AUTO| MANual AUTO Clock rate is retrieved from the generated waveform. MANual Clock rate is user-defined
		"""
		response = self._core.io.query_str('SCENario:OUTPut:CLOCk:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AutoManualMode)

	def set_mode(self, mode: enums.AutoManualMode) -> None:
		"""SCPI: SCENario:OUTPut:CLOCk:MODE \n
		Snippet: driver.scenario.output.clock.set_mode(mode = enums.AutoManualMode.AUTO) \n
		Sets the clock mode. \n
			:param mode: AUTO| MANual AUTO Clock rate is retrieved from the generated waveform. MANual Clock rate is user-defined
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.AutoManualMode)
		self._core.io.write(f'SCENario:OUTPut:CLOCk:MODE {param}')

	def get_user(self) -> float:
		"""SCPI: SCENario:OUTPut:CLOCk:USER \n
		Snippet: value: float = driver.scenario.output.clock.get_user() \n
		Sets a user defined clock rate. \n
			:return: user: float Range: 1 to 2.4e+09
		"""
		response = self._core.io.query_str('SCENario:OUTPut:CLOCk:USER?')
		return Conversions.str_to_float(response)

	def set_user(self, user: float) -> None:
		"""SCPI: SCENario:OUTPut:CLOCk:USER \n
		Snippet: driver.scenario.output.clock.set_user(user = 1.0) \n
		Sets a user defined clock rate. \n
			:param user: float Range: 1 to 2.4e+09
		"""
		param = Conversions.decimal_value_to_str(user)
		self._core.io.write(f'SCENario:OUTPut:CLOCk:USER {param}')

	def clone(self) -> 'Clock':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Clock(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
