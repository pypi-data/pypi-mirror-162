from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Rec:
	"""Rec commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rec", core, parent)

	# noinspection PyTypeChecker
	def get_pmode(self) -> enums.Pmode:
		"""SCPI: SCENario:DF:LOCation:REC:PMODe \n
		Snippet: value: enums.Pmode = driver.scenario.df.location.rec.get_pmode() \n
		Sets if the receiver is static or moving. \n
			:return: pmode: STATic| MOVing
		"""
		response = self._core.io.query_str('SCENario:DF:LOCation:REC:PMODe?')
		return Conversions.str_to_scalar_enum(response, enums.Pmode)

	def set_pmode(self, pmode: enums.Pmode) -> None:
		"""SCPI: SCENario:DF:LOCation:REC:PMODe \n
		Snippet: driver.scenario.df.location.rec.set_pmode(pmode = enums.Pmode.MOVing) \n
		Sets if the receiver is static or moving. \n
			:param pmode: STATic| MOVing
		"""
		param = Conversions.enum_scalar_to_str(pmode, enums.Pmode)
		self._core.io.write(f'SCENario:DF:LOCation:REC:PMODe {param}')
