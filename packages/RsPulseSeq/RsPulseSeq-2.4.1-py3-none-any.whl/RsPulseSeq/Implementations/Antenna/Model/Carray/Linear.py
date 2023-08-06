from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Linear:
	"""Linear commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("linear", core, parent)

	def get_distance(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:LINear:DISTance \n
		Snippet: value: float = driver.antenna.model.carray.linear.get_distance() \n
		Sets the spacing between the elements of the array antenna. \n
			:return: distance: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:LINear:DISTance?')
		return Conversions.str_to_float(response)

	def set_distance(self, distance: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:LINear:DISTance \n
		Snippet: driver.antenna.model.carray.linear.set_distance(distance = 1.0) \n
		Sets the spacing between the elements of the array antenna. \n
			:param distance: float Range: 0.0001 to 1
		"""
		param = Conversions.decimal_value_to_str(distance)
		self._core.io.write(f'ANTenna:MODel:CARRay:LINear:DISTance {param}')

	def get_n(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:LINear:N \n
		Snippet: value: float = driver.antenna.model.carray.linear.get_n() \n
		Sets the number of elements of the antenna array. \n
			:return: n: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:LINear:N?')
		return Conversions.str_to_float(response)

	def set_n(self, n: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:LINear:N \n
		Snippet: driver.antenna.model.carray.linear.set_n(n = 1.0) \n
		Sets the number of elements of the antenna array. \n
			:param n: float Range: 2 to 1000 (planar phased array; linear phase array) , 100 (rectangular phase array) , 50 (hexagonal phase array)
		"""
		param = Conversions.decimal_value_to_str(n)
		self._core.io.write(f'ANTenna:MODel:CARRay:LINear:N {param}')
