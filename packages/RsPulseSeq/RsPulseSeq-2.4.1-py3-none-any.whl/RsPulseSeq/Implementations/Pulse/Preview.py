from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Preview:
	"""Preview commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("preview", core, parent)

	def set_mode(self, mode: enums.PreviewMode) -> None:
		"""SCPI: PULSe:PREView:MODE \n
		Snippet: driver.pulse.preview.set_mode(mode = enums.PreviewMode.ENVelope) \n
		Switches between the envelope and modulation graphs. \n
			:param mode: ENVelope| MOP
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.PreviewMode)
		self._core.io.write(f'PULSe:PREView:MODE {param}')

	def set_mop(self, mop: enums.PreviewMop) -> None:
		"""SCPI: PULSe:PREView:MOP \n
		Snippet: driver.pulse.preview.set_mop(mop = enums.PreviewMop.FREQuency) \n
		Sets the displayed modulation characteristics. \n
			:param mop: IQ| PHASe| FREQuency
		"""
		param = Conversions.enum_scalar_to_str(mop, enums.PreviewMop)
		self._core.io.write(f'PULSe:PREView:MOP {param}')
