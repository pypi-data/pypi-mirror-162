from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Custom:
	"""Custom commands group definition. 6 total commands, 1 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("custom", core, parent)

	@property
	def hpBw(self):
		"""hpBw commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_hpBw'):
			from .HpBw import HpBw
			self._hpBw = HpBw(self._core, self._cmd_group)
		return self._hpBw

	def get_sl_rolloff(self) -> float:
		"""SCPI: ANTenna:MODel:CUSTom:SLRolloff \n
		Snippet: value: float = driver.antenna.model.custom.get_sl_rolloff() \n
		Sets the factor used to calculate the HPBW of the side lobes. \n
			:return: sl_rolloff: float Range: 1 to 45
		"""
		response = self._core.io.query_str('ANTenna:MODel:CUSTom:SLRolloff?')
		return Conversions.str_to_float(response)

	def set_sl_rolloff(self, sl_rolloff: float) -> None:
		"""SCPI: ANTenna:MODel:CUSTom:SLRolloff \n
		Snippet: driver.antenna.model.custom.set_sl_rolloff(sl_rolloff = 1.0) \n
		Sets the factor used to calculate the HPBW of the side lobes. \n
			:param sl_rolloff: float Range: 1 to 45
		"""
		param = Conversions.decimal_value_to_str(sl_rolloff)
		self._core.io.write(f'ANTenna:MODel:CUSTom:SLRolloff {param}')

	def get_sl_scale(self) -> float:
		"""SCPI: ANTenna:MODel:CUSTom:SLSCale \n
		Snippet: value: float = driver.antenna.model.custom.get_sl_scale() \n
		Sets the step size to calculate the power level of the side lobes. \n
			:return: sl_scale: float Range: 0.01 to 10
		"""
		response = self._core.io.query_str('ANTenna:MODel:CUSTom:SLSCale?')
		return Conversions.str_to_float(response)

	def set_sl_scale(self, sl_scale: float) -> None:
		"""SCPI: ANTenna:MODel:CUSTom:SLSCale \n
		Snippet: driver.antenna.model.custom.set_sl_scale(sl_scale = 1.0) \n
		Sets the step size to calculate the power level of the side lobes. \n
			:param sl_scale: float Range: 0.01 to 10
		"""
		param = Conversions.decimal_value_to_str(sl_scale)
		self._core.io.write(f'ANTenna:MODel:CUSTom:SLSCale {param}')

	def get_sl_start(self) -> float:
		"""SCPI: ANTenna:MODel:CUSTom:SLSTart \n
		Snippet: value: float = driver.antenna.model.custom.get_sl_start() \n
		Sets the power level of the first pairs of side lobes. \n
			:return: sl_start: float Range: 1 to 90
		"""
		response = self._core.io.query_str('ANTenna:MODel:CUSTom:SLSTart?')
		return Conversions.str_to_float(response)

	def set_sl_start(self, sl_start: float) -> None:
		"""SCPI: ANTenna:MODel:CUSTom:SLSTart \n
		Snippet: driver.antenna.model.custom.set_sl_start(sl_start = 1.0) \n
		Sets the power level of the first pairs of side lobes. \n
			:param sl_start: float Range: 1 to 90
		"""
		param = Conversions.decimal_value_to_str(sl_start)
		self._core.io.write(f'ANTenna:MODel:CUSTom:SLSTart {param}')

	def get_resolution(self) -> float:
		"""SCPI: ANTenna:MODel:CUSTom:RESolution \n
		Snippet: value: float = driver.antenna.model.custom.get_resolution() \n
		Sets a custom resolution for the antenna pattern simulation. \n
			:return: resolution: float Range: 0.1 to 1
		"""
		response = self._core.io.query_str('ANTenna:MODel:CUSTom:RESolution?')
		return Conversions.str_to_float(response)

	def set_resolution(self, resolution: float) -> None:
		"""SCPI: ANTenna:MODel:CUSTom:RESolution \n
		Snippet: driver.antenna.model.custom.set_resolution(resolution = 1.0) \n
		Sets a custom resolution for the antenna pattern simulation. \n
			:param resolution: float Range: 0.1 to 1
		"""
		param = Conversions.decimal_value_to_str(resolution)
		self._core.io.write(f'ANTenna:MODel:CUSTom:RESolution {param}')

	def clone(self) -> 'Custom':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Custom(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
