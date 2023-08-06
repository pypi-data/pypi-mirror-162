from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Overshoot:
	"""Overshoot commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("overshoot", core, parent)

	def get_decay(self) -> float:
		"""SCPI: PULSe:OVERshoot:DECay \n
		Snippet: value: float = driver.pulse.overshoot.get_decay() \n
		Sets the number of peaks. \n
			:return: decay: float Range: 1 to 100
		"""
		response = self._core.io.query_str('PULSe:OVERshoot:DECay?')
		return Conversions.str_to_float(response)

	def set_decay(self, decay: float) -> None:
		"""SCPI: PULSe:OVERshoot:DECay \n
		Snippet: driver.pulse.overshoot.set_decay(decay = 1.0) \n
		Sets the number of peaks. \n
			:param decay: float Range: 1 to 100
		"""
		param = Conversions.decimal_value_to_str(decay)
		self._core.io.write(f'PULSe:OVERshoot:DECay {param}')

	def get_value(self) -> float:
		"""SCPI: PULSe:OVERshoot \n
		Snippet: value: float = driver.pulse.overshoot.get_value() \n
		Sets the overshoot level value. \n
			:return: overshoot: float Range: 0 to 50
		"""
		response = self._core.io.query_str('PULSe:OVERshoot?')
		return Conversions.str_to_float(response)

	def set_value(self, overshoot: float) -> None:
		"""SCPI: PULSe:OVERshoot \n
		Snippet: driver.pulse.overshoot.set_value(overshoot = 1.0) \n
		Sets the overshoot level value. \n
			:param overshoot: float Range: 0 to 50
		"""
		param = Conversions.decimal_value_to_str(overshoot)
		self._core.io.write(f'PULSe:OVERshoot {param}')
