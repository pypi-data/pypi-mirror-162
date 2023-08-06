from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Log:
	"""Log commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("log", core, parent)

	def set_min(self, min_py: float) -> None:
		"""SCPI: PLOT:POLar:LOG:MIN \n
		Snippet: driver.plot.polar.log.set_min(min_py = 1.0) \n
		Sets the minimum value displayed on the y axis. \n
			:param min_py: float
		"""
		param = Conversions.decimal_value_to_str(min_py)
		self._core.io.write(f'PLOT:POLar:LOG:MIN {param}')
