from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Random:
	"""Random commands group definition. 9 total commands, 3 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("random", core, parent)

	@property
	def normal(self):
		"""normal commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_normal'):
			from .Normal import Normal
			self._normal = Normal(self._core, self._cmd_group)
		return self._normal

	@property
	def u(self):
		"""u commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_u'):
			from .U import U
			self._u = U(self._core, self._cmd_group)
		return self._u

	@property
	def uniform(self):
		"""uniform commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_uniform'):
			from .Uniform import Uniform
			self._uniform = Uniform(self._core, self._cmd_group)
		return self._uniform

	# noinspection PyTypeChecker
	def get_distribution(self) -> enums.RandomDistribution:
		"""SCPI: IPM:RANDom:DISTribution \n
		Snippet: value: enums.RandomDistribution = driver.ipm.random.get_distribution() \n
		Sets the distribution function. \n
			:return: distribution: UNIForm| NORMal| U
		"""
		response = self._core.io.query_str('IPM:RANDom:DISTribution?')
		return Conversions.str_to_scalar_enum(response, enums.RandomDistribution)

	def set_distribution(self, distribution: enums.RandomDistribution) -> None:
		"""SCPI: IPM:RANDom:DISTribution \n
		Snippet: driver.ipm.random.set_distribution(distribution = enums.RandomDistribution.NORMal) \n
		Sets the distribution function. \n
			:param distribution: UNIForm| NORMal| U
		"""
		param = Conversions.enum_scalar_to_str(distribution, enums.RandomDistribution)
		self._core.io.write(f'IPM:RANDom:DISTribution {param}')

	def clone(self) -> 'Random':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Random(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
