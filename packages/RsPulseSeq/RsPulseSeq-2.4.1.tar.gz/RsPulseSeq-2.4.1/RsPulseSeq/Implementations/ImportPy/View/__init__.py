from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class View:
	"""View commands group definition. 6 total commands, 2 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("view", core, parent)

	@property
	def move(self):
		"""move commands group. 3 Sub-classes, 1 commands."""
		if not hasattr(self, '_move'):
			from .Move import Move
			self._move = Move(self._core, self._cmd_group)
		return self._move

	@property
	def time(self):
		"""time commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_time'):
			from .Time import Time
			self._time = Time(self._core, self._cmd_group)
		return self._time

	# noinspection PyTypeChecker
	def get_count(self) -> enums.ViewCount:
		"""SCPI: IMPort:VIEW:COUNt \n
		Snippet: value: enums.ViewCount = driver.importPy.view.get_count() \n
		Sets the entries per page to be displayed. \n
			:return: count: 50| 100| 500| 1000| 5000| 10000| 50000| 100000
		"""
		response = self._core.io.query_str('IMPort:VIEW:COUNt?')
		return Conversions.str_to_scalar_enum(response, enums.ViewCount)

	def set_count(self, count: enums.ViewCount) -> None:
		"""SCPI: IMPort:VIEW:COUNt \n
		Snippet: driver.importPy.view.set_count(count = enums.ViewCount._100) \n
		Sets the entries per page to be displayed. \n
			:param count: 50| 100| 500| 1000| 5000| 10000| 50000| 100000
		"""
		param = Conversions.enum_scalar_to_str(count, enums.ViewCount)
		self._core.io.write(f'IMPort:VIEW:COUNt {param}')

	def clone(self) -> 'View':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = View(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
