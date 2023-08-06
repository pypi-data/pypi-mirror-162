from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Sinc:
	"""Sinc commands group definition. 3 total commands, 1 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sinc", core, parent)

	@property
	def hpBw(self):
		"""hpBw commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_hpBw'):
			from .HpBw import HpBw
			self._hpBw = HpBw(self._core, self._cmd_group)
		return self._hpBw

	def get_resolution(self) -> float:
		"""SCPI: ANTenna:MODel:SINC:RESolution \n
		Snippet: value: float = driver.antenna.model.sinc.get_resolution() \n
		Sets a custom resolution for the antenna pattern simulation. \n
			:return: resolution: float Range: 0.1 to 1
		"""
		response = self._core.io.query_str('ANTenna:MODel:SINC:RESolution?')
		return Conversions.str_to_float(response)

	def set_resolution(self, resolution: float) -> None:
		"""SCPI: ANTenna:MODel:SINC:RESolution \n
		Snippet: driver.antenna.model.sinc.set_resolution(resolution = 1.0) \n
		Sets a custom resolution for the antenna pattern simulation. \n
			:param resolution: float Range: 0.1 to 1
		"""
		param = Conversions.decimal_value_to_str(resolution)
		self._core.io.write(f'ANTenna:MODel:SINC:RESolution {param}')

	def clone(self) -> 'Sinc':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Sinc(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
