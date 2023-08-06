from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SoQpsk:
	"""SoQpsk commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("soQpsk", core, parent)

	def get_irig(self) -> bool:
		"""SCPI: PULSe:MOP:QPSK:SOQPsk:IRIG \n
		Snippet: value: bool = driver.pulse.mop.qpsk.soQpsk.get_irig() \n
		Enables differential encoding according to the telemetry standard IRIG 106-04. \n
			:return: irig: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PULSe:MOP:QPSK:SOQPsk:IRIG?')
		return Conversions.str_to_bool(response)

	def set_irig(self, irig: bool) -> None:
		"""SCPI: PULSe:MOP:QPSK:SOQPsk:IRIG \n
		Snippet: driver.pulse.mop.qpsk.soQpsk.set_irig(irig = False) \n
		Enables differential encoding according to the telemetry standard IRIG 106-04. \n
			:param irig: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(irig)
		self._core.io.write(f'PULSe:MOP:QPSK:SOQPsk:IRIG {param}')
