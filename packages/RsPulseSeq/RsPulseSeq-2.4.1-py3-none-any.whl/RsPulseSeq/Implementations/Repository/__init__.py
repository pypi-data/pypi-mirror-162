from typing import List

from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Repository:
	"""Repository commands group definition. 17 total commands, 2 Subgroups, 15 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("repository", core, parent)

	@property
	def volatile(self):
		"""volatile commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_volatile'):
			from .Volatile import Volatile
			self._volatile = Volatile(self._core, self._cmd_group)
		return self._volatile

	@property
	def xpol(self):
		"""xpol commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_xpol'):
			from .Xpol import Xpol
			self._xpol = Xpol(self._core, self._cmd_group)
		return self._xpol

	# noinspection PyTypeChecker
	def get_complexity(self) -> enums.Complexity:
		"""SCPI: REPository:COMPlexity \n
		Snippet: value: enums.Complexity = driver.repository.get_complexity() \n
		Sets the complexity level. \n
			:return: complexity: PTRain| EMITter| DIRection
		"""
		response = self._core.io.query_str('REPository:COMPlexity?')
		return Conversions.str_to_scalar_enum(response, enums.Complexity)

	def set_complexity(self, complexity: enums.Complexity) -> None:
		"""SCPI: REPository:COMPlexity \n
		Snippet: driver.repository.set_complexity(complexity = enums.Complexity.DIRection) \n
		Sets the complexity level. \n
			:param complexity: PTRain| EMITter| DIRection
		"""
		param = Conversions.enum_scalar_to_str(complexity, enums.Complexity)
		self._core.io.write(f'REPository:COMPlexity {param}')

	def get_access(self) -> str:
		"""SCPI: REPository:ACCess \n
		Snippet: value: str = driver.repository.get_access() \n
		Queries information on the access rights of the current user. \n
			:return: access: permission,login,pass,Uname permission Permission of the current user, for example RW (read-write) login,pass Login/Pass=No: Password not required Login/Pass=Yes: Password required Uname User name of the current user
		"""
		response = self._core.io.query_str('REPository:ACCess?')
		return trim_str_response(response)

	def get_author(self) -> str:
		"""SCPI: REPository:AUTHor \n
		Snippet: value: str = driver.repository.get_author() \n
		Enters information on the author. \n
			:return: author: string
		"""
		response = self._core.io.query_str('REPository:AUTHor?')
		return trim_str_response(response)

	def set_author(self, author: str) -> None:
		"""SCPI: REPository:AUTHor \n
		Snippet: driver.repository.set_author(author = '1') \n
		Enters information on the author. \n
			:param author: string
		"""
		param = Conversions.value_to_quoted_str(author)
		self._core.io.write(f'REPository:AUTHor {param}')

	def get_catalog(self) -> str:
		"""SCPI: REPository:CATalog \n
		Snippet: value: str = driver.repository.get_catalog() \n
		Queries the available repository elements in the database. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('REPository:CATalog?')
		return trim_str_response(response)

	def get_comment(self) -> str:
		"""SCPI: REPository:COMMent \n
		Snippet: value: str = driver.repository.get_comment() \n
		Adds a description to the selected repository element. \n
			:return: comment: string
		"""
		response = self._core.io.query_str('REPository:COMMent?')
		return trim_str_response(response)

	def set_comment(self, comment: str) -> None:
		"""SCPI: REPository:COMMent \n
		Snippet: driver.repository.set_comment(comment = '1') \n
		Adds a description to the selected repository element. \n
			:param comment: string
		"""
		param = Conversions.value_to_quoted_str(comment)
		self._core.io.write(f'REPository:COMMent {param}')

	def set_create(self, create: List[int]) -> None:
		"""SCPI: REPository:CREate \n
		Snippet: driver.repository.set_create(create = [1, 2, 3]) \n
		Creates a repository element with the selected name. \n
			:param create: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.list_to_csv_str(create)
		self._core.io.write(f'REPository:CREate {param}')

	def get_date(self) -> str:
		"""SCPI: REPository:DATE \n
		Snippet: value: str = driver.repository.get_date() \n
		Queries the creation data. \n
			:return: date: string
		"""
		response = self._core.io.query_str('REPository:DATE?')
		return trim_str_response(response)

	def set_date(self, date: str) -> None:
		"""SCPI: REPository:DATE \n
		Snippet: driver.repository.set_date(date = '1') \n
		Queries the creation data. \n
			:param date: string
		"""
		param = Conversions.value_to_quoted_str(date)
		self._core.io.write(f'REPository:DATE {param}')

	def get_filename(self) -> str:
		"""SCPI: REPository:FILename \n
		Snippet: value: str = driver.repository.get_filename() \n
		Queries the file name of the repository archive. \n
			:return: filename: string File path, incl. file name, and extension
		"""
		response = self._core.io.query_str('REPository:FILename?')
		return trim_str_response(response)

	def get_path(self) -> str:
		"""SCPI: REPository:PATH \n
		Snippet: value: str = driver.repository.get_path() \n
		Queries the directory in that the repository archive is stored. \n
			:return: path: string
		"""
		response = self._core.io.query_str('REPository:PATH?')
		return trim_str_response(response)

	def set_remove(self, remove: str) -> None:
		"""SCPI: REPository:REMove \n
		Snippet: driver.repository.set_remove(remove = '1') \n
		Removes the selected element from the workspace. The element must not reference any child elements. Remove the referenced
		elements first. \n
			:param remove: No help available
		"""
		param = Conversions.value_to_quoted_str(remove)
		self._core.io.write(f'REPository:REMove {param}')

	def save(self) -> None:
		"""SCPI: REPository:SAVE \n
		Snippet: driver.repository.save() \n
		Stores the repository archive. To query the storage location, use the command method RsPulseSeq.Repository.path. \n
		"""
		self._core.io.write(f'REPository:SAVE')

	def save_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: REPository:SAVE \n
		Snippet: driver.repository.save_with_opc() \n
		Stores the repository archive. To query the storage location, use the command method RsPulseSeq.Repository.path. \n
		Same as save, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'REPository:SAVE', opc_timeout_ms)

	# noinspection PyTypeChecker
	def get_security(self) -> enums.SecurityLevel:
		"""SCPI: REPository:SECurity \n
		Snippet: value: enums.SecurityLevel = driver.repository.get_security() \n
		Sets the security level. \n
			:return: security: LEV0| LEV1| LEV2| LEV3| LEV4
		"""
		response = self._core.io.query_str('REPository:SECurity?')
		return Conversions.str_to_scalar_enum(response, enums.SecurityLevel)

	def set_security(self, security: enums.SecurityLevel) -> None:
		"""SCPI: REPository:SECurity \n
		Snippet: driver.repository.set_security(security = enums.SecurityLevel.LEV0) \n
		Sets the security level. \n
			:param security: LEV0| LEV1| LEV2| LEV3| LEV4
		"""
		param = Conversions.enum_scalar_to_str(security, enums.SecurityLevel)
		self._core.io.write(f'REPository:SECurity {param}')

	def get_select(self) -> str:
		"""SCPI: REPository:SELect \n
		Snippet: value: str = driver.repository.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('REPository:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: REPository:SELect \n
		Snippet: driver.repository.set_select(select = '1') \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'REPository:SELect {param}')

	def get_uuid(self) -> str:
		"""SCPI: REPository:UUID \n
		Snippet: value: str = driver.repository.get_uuid() \n
		Queries the repository's Universally Unique Identifier (UUID) . \n
			:return: uuid: string
		"""
		response = self._core.io.query_str('REPository:UUID?')
		return trim_str_response(response)

	def get_version(self) -> str:
		"""SCPI: REPository:VERSion \n
		Snippet: value: str = driver.repository.get_version() \n
		Sets the repository version. \n
			:return: version: string
		"""
		response = self._core.io.query_str('REPository:VERSion?')
		return trim_str_response(response)

	def set_version(self, version: str) -> None:
		"""SCPI: REPository:VERSion \n
		Snippet: driver.repository.set_version(version = '1') \n
		Sets the repository version. \n
			:param version: string
		"""
		param = Conversions.value_to_quoted_str(version)
		self._core.io.write(f'REPository:VERSion {param}')

	def clone(self) -> 'Repository':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Repository(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
