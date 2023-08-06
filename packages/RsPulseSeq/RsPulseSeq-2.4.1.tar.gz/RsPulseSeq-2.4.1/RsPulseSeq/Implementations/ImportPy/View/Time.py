from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Time:
	"""Time commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("time", core, parent)

	def get_start(self) -> float:
		"""SCPI: IMPort:VIEW:TIME:STARt \n
		Snippet: value: float = driver.importPy.view.time.get_start() \n
		Sets the start line displayed on the page. \n
			:return: start: float
		"""
		response = self._core.io.query_str('IMPort:VIEW:TIME:STARt?')
		return Conversions.str_to_float(response)

	def set_start(self, start: float) -> None:
		"""SCPI: IMPort:VIEW:TIME:STARt \n
		Snippet: driver.importPy.view.time.set_start(start = 1.0) \n
		Sets the start line displayed on the page. \n
			:param start: float
		"""
		param = Conversions.decimal_value_to_str(start)
		self._core.io.write(f'IMPort:VIEW:TIME:STARt {param}')
