from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Level:
	"""Level commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("level", core, parent)

	def get_range(self) -> float:
		"""SCPI: WAVeform:BEMitter:LEVel:RANGe \n
		Snippet: value: float = driver.waveform.bemitter.level.get_range() \n
		Sets the maximum level difference between the strongest and the weakest emitter. \n
			:return: range_py: float Range: 0 to 90
		"""
		response = self._core.io.query_str('WAVeform:BEMitter:LEVel:RANGe?')
		return Conversions.str_to_float(response)

	def set_range(self, range_py: float) -> None:
		"""SCPI: WAVeform:BEMitter:LEVel:RANGe \n
		Snippet: driver.waveform.bemitter.level.set_range(range_py = 1.0) \n
		Sets the maximum level difference between the strongest and the weakest emitter. \n
			:param range_py: float Range: 0 to 90
		"""
		param = Conversions.decimal_value_to_str(range_py)
		self._core.io.write(f'WAVeform:BEMitter:LEVel:RANGe {param}')
