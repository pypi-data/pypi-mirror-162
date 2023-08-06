from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RamBuff:
	"""RamBuff commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ramBuff", core, parent)

	# noinspection PyTypeChecker
	def get_size(self) -> enums.BufferSize:
		"""SCPI: PROGram:RAMBuff:SIZE \n
		Snippet: value: enums.BufferSize = driver.program.ramBuff.get_size() \n
		Sets the ARB RAM buffer size. \n
			:return: size: 16M| 64M| 128M| 256M| 512M| 1G
		"""
		response = self._core.io.query_str('PROGram:RAMBuff:SIZE?')
		return Conversions.str_to_scalar_enum(response, enums.BufferSize)

	def set_size(self, size: enums.BufferSize) -> None:
		"""SCPI: PROGram:RAMBuff:SIZE \n
		Snippet: driver.program.ramBuff.set_size(size = enums.BufferSize._128M) \n
		Sets the ARB RAM buffer size. \n
			:param size: 16M| 64M| 128M| 256M| 512M| 1G
		"""
		param = Conversions.enum_scalar_to_str(size, enums.BufferSize)
		self._core.io.write(f'PROGram:RAMBuff:SIZE {param}')
