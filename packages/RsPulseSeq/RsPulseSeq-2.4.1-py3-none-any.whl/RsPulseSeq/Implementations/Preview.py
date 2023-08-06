from ..Internal.Core import Core
from ..Internal.CommandsGroup import CommandsGroup
from ..Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Preview:
	"""Preview commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("preview", core, parent)

	def get_position(self) -> str:
		"""SCPI: PREView:POSition \n
		Snippet: value: str = driver.preview.get_position() \n
		If movement is enabled, queries the current positions of the Tx items. \n
			:return: position: string Semicolon-separated string with the format: TIME=time_from_simulation_start; ID=Tx item ID;NAME=Tx item alias name;DIST=distancekm;LEVATT=Level at Rx origindBm;AZI=Azimuthdeg;ELEV=Elevationdeg;N=Northkm;E=Eastkm;H=Heightkm;
		"""
		response = self._core.io.query_str('PREView:POSition?')
		return trim_str_response(response)
