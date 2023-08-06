from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Dsrc:
	"""Dsrc commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dsrc", core, parent)

	def get_reset(self) -> bool:
		"""SCPI: PULSe:MOP:DATA:DSRC:RESet \n
		Snippet: value: bool = driver.pulse.mop.data.dsrc.get_reset() \n
		Resets the data source at the end of the pulse. \n
			:return: reset: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PULSe:MOP:DATA:DSRC:RESet?')
		return Conversions.str_to_bool(response)

	def set_reset(self, reset: bool) -> None:
		"""SCPI: PULSe:MOP:DATA:DSRC:RESet \n
		Snippet: driver.pulse.mop.data.dsrc.set_reset(reset = False) \n
		Resets the data source at the end of the pulse. \n
			:param reset: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(reset)
		self._core.io.write(f'PULSe:MOP:DATA:DSRC:RESet {param}')

	def get_value(self) -> str:
		"""SCPI: PULSe:MOP:DATA:DSRC \n
		Snippet: value: str = driver.pulse.mop.data.dsrc.get_value() \n
		Selects the data source for the modulation, see method RsPulseSeq.Dsrc.create. \n
			:return: dsrc: string
		"""
		response = self._core.io.query_str('PULSe:MOP:DATA:DSRC?')
		return trim_str_response(response)

	def set_value(self, dsrc: str) -> None:
		"""SCPI: PULSe:MOP:DATA:DSRC \n
		Snippet: driver.pulse.mop.data.dsrc.set_value(dsrc = '1') \n
		Selects the data source for the modulation, see method RsPulseSeq.Dsrc.create. \n
			:param dsrc: string
		"""
		param = Conversions.value_to_quoted_str(dsrc)
		self._core.io.write(f'PULSe:MOP:DATA:DSRC {param}')
