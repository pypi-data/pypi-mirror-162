from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Details:
	"""Details commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("details", core, parent)

	def get_albs(self) -> bool:
		"""SCPI: SCENario:OUTPut:ARB:DETails:ALBS \n
		Snippet: value: bool = driver.scenario.output.arb.details.get_albs() \n
		Enables you to calculate the antenna attenuation for each sample. Otherwise a lookup at center position is used. \n
			:return: albs: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:OUTPut:ARB:DETails:ALBS?')
		return Conversions.str_to_bool(response)

	def set_albs(self, albs: bool) -> None:
		"""SCPI: SCENario:OUTPut:ARB:DETails:ALBS \n
		Snippet: driver.scenario.output.arb.details.set_albs(albs = False) \n
		Enables you to calculate the antenna attenuation for each sample. Otherwise a lookup at center position is used. \n
			:param albs: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(albs)
		self._core.io.write(f'SCENario:OUTPut:ARB:DETails:ALBS {param}')
