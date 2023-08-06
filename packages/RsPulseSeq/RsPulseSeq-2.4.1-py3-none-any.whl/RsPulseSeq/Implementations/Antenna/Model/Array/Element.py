from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Element:
	"""Element commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("element", core, parent)

	def get_cosine(self) -> bool:
		"""SCPI: ANTenna:MODel:ARRay:ELEMent:COSine \n
		Snippet: value: bool = driver.antenna.model.array.element.get_cosine() \n
		Sets the characteristic of individual antenna elements. \n
			:return: cosine: ON| OFF| 1| 0 0|OFF Omnidirectional characteristic 1|ON Cosine characteristic
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:ELEMent:COSine?')
		return Conversions.str_to_bool(response)

	def set_cosine(self, cosine: bool) -> None:
		"""SCPI: ANTenna:MODel:ARRay:ELEMent:COSine \n
		Snippet: driver.antenna.model.array.element.set_cosine(cosine = False) \n
		Sets the characteristic of individual antenna elements. \n
			:param cosine: ON| OFF| 1| 0 0|OFF Omnidirectional characteristic 1|ON Cosine characteristic
		"""
		param = Conversions.bool_to_str(cosine)
		self._core.io.write(f'ANTenna:MODel:ARRay:ELEMent:COSine {param}')
