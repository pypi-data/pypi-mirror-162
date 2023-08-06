from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Bemitter:
	"""Bemitter commands group definition. 8 total commands, 3 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("bemitter", core, parent)

	@property
	def level(self):
		"""level commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_level'):
			from .Level import Level
			self._level = Level(self._core, self._cmd_group)
		return self._level

	@property
	def pri(self):
		"""pri commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_pri'):
			from .Pri import Pri
			self._pri = Pri(self._core, self._cmd_group)
		return self._pri

	@property
	def pw(self):
		"""pw commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_pw'):
			from .Pw import Pw
			self._pw = Pw(self._core, self._cmd_group)
		return self._pw

	def get_bandwidth(self) -> float:
		"""SCPI: WAVeform:BEMitter:BWIDth \n
		Snippet: value: float = driver.waveform.bemitter.get_bandwidth() \n
		Sets the maximum permissible bandwidth of the resulting signal. \n
			:return: bwidth: float Range: 1000 to 2e+09
		"""
		response = self._core.io.query_str('WAVeform:BEMitter:BWIDth?')
		return Conversions.str_to_float(response)

	def set_bandwidth(self, bwidth: float) -> None:
		"""SCPI: WAVeform:BEMitter:BWIDth \n
		Snippet: driver.waveform.bemitter.set_bandwidth(bwidth = 1.0) \n
		Sets the maximum permissible bandwidth of the resulting signal. \n
			:param bwidth: float Range: 1000 to 2e+09
		"""
		param = Conversions.decimal_value_to_str(bwidth)
		self._core.io.write(f'WAVeform:BEMitter:BWIDth {param}')

	def get_count(self) -> float:
		"""SCPI: WAVeform:BEMitter:COUNt \n
		Snippet: value: float = driver.waveform.bemitter.get_count() \n
		Sets the number of background emitters. \n
			:return: count: integer Range: 1 to 255
		"""
		response = self._core.io.query_str('WAVeform:BEMitter:COUNt?')
		return Conversions.str_to_float(response)

	def set_count(self, count: float) -> None:
		"""SCPI: WAVeform:BEMitter:COUNt \n
		Snippet: driver.waveform.bemitter.set_count(count = 1.0) \n
		Sets the number of background emitters. \n
			:param count: integer Range: 1 to 255
		"""
		param = Conversions.decimal_value_to_str(count)
		self._core.io.write(f'WAVeform:BEMitter:COUNt {param}')

	def get_duration(self) -> float:
		"""SCPI: WAVeform:BEMitter:DURation \n
		Snippet: value: float = driver.waveform.bemitter.get_duration() \n
		Sets the signal duration. \n
			:return: duration: float Range: 0.0001 to 1
		"""
		response = self._core.io.query_str('WAVeform:BEMitter:DURation?')
		return Conversions.str_to_float(response)

	def set_duration(self, duration: float) -> None:
		"""SCPI: WAVeform:BEMitter:DURation \n
		Snippet: driver.waveform.bemitter.set_duration(duration = 1.0) \n
		Sets the signal duration. \n
			:param duration: float Range: 0.0001 to 1
		"""
		param = Conversions.decimal_value_to_str(duration)
		self._core.io.write(f'WAVeform:BEMitter:DURation {param}')

	def clone(self) -> 'Bemitter':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Bemitter(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
