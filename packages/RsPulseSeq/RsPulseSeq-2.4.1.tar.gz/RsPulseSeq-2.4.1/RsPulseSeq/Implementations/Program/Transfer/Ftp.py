from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Ftp:
	"""Ftp commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ftp", core, parent)

	# noinspection PyTypeChecker
	def get_block_size(self) -> enums.BlockSize:
		"""SCPI: PROGram:TRANsfer:FTP:BLOCksize \n
		Snippet: value: enums.BlockSize = driver.program.transfer.ftp.get_block_size() \n
		Block size used for data transfer. \n
			:return: block_size: 16K| 32K| 64K| 1M| 2M| 4M
		"""
		response = self._core.io.query_str('PROGram:TRANsfer:FTP:BLOCksize?')
		return Conversions.str_to_scalar_enum(response, enums.BlockSize)

	def set_block_size(self, block_size: enums.BlockSize) -> None:
		"""SCPI: PROGram:TRANsfer:FTP:BLOCksize \n
		Snippet: driver.program.transfer.ftp.set_block_size(block_size = enums.BlockSize._16K) \n
		Block size used for data transfer. \n
			:param block_size: 16K| 32K| 64K| 1M| 2M| 4M
		"""
		param = Conversions.enum_scalar_to_str(block_size, enums.BlockSize)
		self._core.io.write(f'PROGram:TRANsfer:FTP:BLOCksize {param}')

	def get_enable(self) -> bool:
		"""SCPI: PROGram:TRANsfer:FTP:ENABle \n
		Snippet: value: bool = driver.program.transfer.ftp.get_enable() \n
		Enables an FTP data transfer for transfer of large files to the processing instrument. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PROGram:TRANsfer:FTP:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: PROGram:TRANsfer:FTP:ENABle \n
		Snippet: driver.program.transfer.ftp.set_enable(enable = False) \n
		Enables an FTP data transfer for transfer of large files to the processing instrument. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'PROGram:TRANsfer:FTP:ENABle {param}')

	def get_passwd(self) -> str:
		"""SCPI: PROGram:TRANsfer:FTP:PASSwd \n
		Snippet: value: str = driver.program.transfer.ftp.get_passwd() \n
		No command help available \n
			:return: passwd: string
		"""
		response = self._core.io.query_str('PROGram:TRANsfer:FTP:PASSwd?')
		return trim_str_response(response)

	def set_passwd(self, passwd: str) -> None:
		"""SCPI: PROGram:TRANsfer:FTP:PASSwd \n
		Snippet: driver.program.transfer.ftp.set_passwd(passwd = '1') \n
		No command help available \n
			:param passwd: string
		"""
		param = Conversions.value_to_quoted_str(passwd)
		self._core.io.write(f'PROGram:TRANsfer:FTP:PASSwd {param}')

	def get_uname(self) -> str:
		"""SCPI: PROGram:TRANsfer:FTP:UNAMe \n
		Snippet: value: str = driver.program.transfer.ftp.get_uname() \n
		Sets the user name and password of the processing instrument. \n
			:return: uname: string
		"""
		response = self._core.io.query_str('PROGram:TRANsfer:FTP:UNAMe?')
		return trim_str_response(response)

	def set_uname(self, uname: str) -> None:
		"""SCPI: PROGram:TRANsfer:FTP:UNAMe \n
		Snippet: driver.program.transfer.ftp.set_uname(uname = '1') \n
		Sets the user name and password of the processing instrument. \n
			:param uname: string
		"""
		param = Conversions.value_to_quoted_str(uname)
		self._core.io.write(f'PROGram:TRANsfer:FTP:UNAMe {param}')
