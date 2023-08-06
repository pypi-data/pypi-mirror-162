from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Direction:
	"""Direction commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("direction", core, parent)

	def get_away(self) -> bool:
		"""SCPI: PLATform:EMITter:DIRection:AWAY \n
		Snippet: value: bool = driver.platform.emitter.direction.get_away() \n
		This command automatically configures the transmission direction of the selected emitter. No effect if emitter is at
		origin. Affects emitters whose position (relative to the origin) has been defined by one of the following methods:
			INTRO_CMD_HELP: Examples of special characters: \n
			- Set X and Y values
			- Set Angle and Radius values
		The transmission direction is configured so that it is directly away from the origin. \n
			:return: away: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PLATform:EMITter:DIRection:AWAY?')
		return Conversions.str_to_bool(response)

	def set_away(self, away: bool) -> None:
		"""SCPI: PLATform:EMITter:DIRection:AWAY \n
		Snippet: driver.platform.emitter.direction.set_away(away = False) \n
		This command automatically configures the transmission direction of the selected emitter. No effect if emitter is at
		origin. Affects emitters whose position (relative to the origin) has been defined by one of the following methods:
			INTRO_CMD_HELP: Examples of special characters: \n
			- Set X and Y values
			- Set Angle and Radius values
		The transmission direction is configured so that it is directly away from the origin. \n
			:param away: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(away)
		self._core.io.write(f'PLATform:EMITter:DIRection:AWAY {param}')
