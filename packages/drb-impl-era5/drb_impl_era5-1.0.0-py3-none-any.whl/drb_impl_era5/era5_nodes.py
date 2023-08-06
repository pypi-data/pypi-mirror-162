from __future__ import annotations

import abc
import re
from enum import Enum
from urllib.parse import urlparse

from drb import DrbNode, AbstractNode
from drb.exceptions import DrbException, DrbNotImplementationException
from drb.path import ParsedPath
from drb.utils.keyringconnection import kr_check, kr_get_auth
from drb_impl_http import DrbHttpNode
from drb.factory import DrbFactoryResolver

from requests.auth import AuthBase
from typing import Optional, List, Union, Any, Dict, Tuple
import cdsapi

from drb_impl_era5 import era5_constants
from drb_impl_era5.era5_predicates import \
    Era5PredicateEra5SingleLevelsByMonth, \
    Era5PredicateEra5Base, Era5PredicateEra5SingleLevelsByHour, \
    Era5PredicateEra5Land, Era5PredicateEra5LandMonthly, \
    Era5PredicateEra5PressureLevelByHour, \
    Era5PredicateEra5PressureLevelsByMonth


class Era5ServiceNodeCommon(AbstractNode, abc.ABC):
    def __init__(self, parent: DrbNode):
        super().__init__()

        self._path = None
        self._parent = parent

    @property
    def path(self) -> ParsedPath:
        if self._path is None:
            if self._parent is None:
                self._path = ParsedPath(f'/{self.name}')
            else:
                self._path = self.parent.path / self.name
        return self._path

    @property
    def namespace_uri(self) -> Optional[str]:
        return 'ERA5'

    @property
    def parent(self) -> Optional[DrbNode]:
        return self._parent

    @property
    def value(self) -> Optional[Any]:
        return None

    def has_impl(self, impl: type) -> bool:
        return False

    def get_impl(self, impl: type, **kwargs) -> Any:
        raise DrbNotImplementationException(
            f"XmlNode doesn't implement {impl}")

    def get_predicate_allowed(self):
        return None

    @property
    @abc.abstractmethod
    def client_cds(self):
        raise NotImplementedError

    def close(self) -> None:
        pass


class Era5ServiceNode(Era5ServiceNodeCommon):
    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return {}

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        raise DrbException(f'No attribute ({name}:{namespace_uri}) found!')

    def __init__(self, path='https://cds.climate.copernicus.eu/api/v2',
                 auth: Union[AuthBase, str] = None):
        super().__init__(None)
        self._children = None

        self._path = path.replace('+era5', '') if '+era5' in path else path
        if len(self._path) == 0:
            self._path = 'https://cds.climate.copernicus.eu/api/v2'
        self._auth = auth

        self._cds = None

    @property
    def name(self) -> str:
        return self._path

    @property
    def path(self) -> ParsedPath:
        return ParsedPath(self._path)

    @property
    def client_cds(self):
        if self._cds is None:
            key = None
            if isinstance(self.auth, str):
                key = self.auth
            elif isinstance(self.auth, AuthBase):
                key = self.auth.username + ':' + self.auth.password
            if key is not None:
                self._cds = cdsapi.Client(
                    url=self._path,
                    key=key, verify=True)
            else:
                self._cds = cdsapi.Client(
                    url=self._path, verify=True)
        return self._cds

    @property
    def auth(self) -> Union[AuthBase, str]:
        if self._auth is not None:
            return self._auth
        if kr_check(self._path):
            return kr_get_auth(self._path)

    @property
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []

            for enum_data_set in DataSetERA5:
                self._children.append(Era5NodeDataSet(self, enum_data_set))

        return self._children


class Era5NodeDataSet(Era5ServiceNodeCommon):

    def __init__(self, parent: Era5ServiceNode, dataset_enum: DataSetERA5):
        super().__init__(parent)

        self._name = dataset_enum.name
        self._children_name = dataset_enum.children
        self._children = None
        self._attributes = None
        self._list_product_type = dataset_enum.list_product_type

        self._predicate_class = dataset_enum.predicate_class

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        if self._attributes is None:
            self._attributes = {
                ('product_type', None): [v for v in self._list_product_type]}
        return self._attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        try:
            return self.attributes[name, namespace_uri]
        except KeyError:
            raise DrbException(f'No attribute ({name}:{namespace_uri}) found!')

    @property
    def client_cds(self):
        return self.parent.client_cds

    @property
    def name(self) -> str:
        return self._name

    @property
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []
            for child_name in self._children_name:
                self._children.append(EraNode(self, child_name))
        return self._children

    def execute_request(self, item):
        res = self.client_cds.retrieve(self.name, item)
        return EraNodeData(self, res.toJSON())

    def __get_item_dict(self, dict_request):
        if 'variable' not in dict_request.keys():
            dict_request['variable'] = self._children_name

        return self.execute_request(dict_request)

    def __getitem__(self, item):
        if isinstance(item, dict):
            return self.__get_item_dict(item)
        elif isinstance(item, Era5PredicateEra5Base):
            return self.__get_item_dict(item.to_dict())
        else:
            return super().__getitem__(item)

    def get_predicate_allowed(self):
        return self._predicate_class


class EraNode(Era5ServiceNodeCommon):

    def __init__(self, parent: Era5ServiceNode, name: str):
        super().__init__(parent)
        self._name = name

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return self.parent.attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        return self.parent.get_attribute(name, namespace_uri)

    @property
    def client_cds(self):
        return self.parent.client_cds

    @property
    def name(self) -> str:
        return self._name

    @property
    def children(self) -> List[DrbNode]:
        return []

    def __getitem__(self, item):
        dict_request = {}
        if isinstance(item, dict):
            dict_request = item
        if isinstance(item, Era5PredicateEra5Base):
            dict_request = item.to_dict()
        if 'variable' not in dict_request.keys():
            dict_request['variable'] = self.name
        return self.parent.execute_request(dict_request)


class EraNodeData(Era5ServiceNodeCommon):

    @property
    def client_cds(self):
        return self.parent.client_cds

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        if self._attributes is None:
            self._attributes = {(k, None): v for k, v in self._res.items()}
        return self._attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        try:
            return self.attributes[name, namespace_uri]
        except KeyError:
            raise DrbException(f'No attribute ({name}:{namespace_uri}) found!')

    @property
    def children(self) -> List[DrbNode]:
        if self._child is None:
            url = self._res['location']
            node = DrbHttpNode(url)

            self._child = DrbFactoryResolver().create(node)

        return [self._child]

    def __init__(self, parent: Era5ServiceNode, res):
        super().__init__(parent)
        self._parent = parent
        self._res = res
        self._attributes = None
        self._child = None

        parsed_uri = urlparse(res['location'])
        self._name = str(parsed_uri.path).split('/')[-1]

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> Optional[Any]:
        return self._res


class DataSetERA5(Enum):
    ERA5_LAND = (
        'reanalysis-era5-land',
        era5_constants.list_predefined_variables_era5_land,
        None,
        Era5PredicateEra5Land)
    ERA5_LAND_MONTHLY = (
        'reanalysis-era5-land-monthly-means',
        era5_constants.list_predefined_variables_era5_land,
        era5_constants.list_product_type_land_monthly,
        Era5PredicateEra5LandMonthly)
    ERA5_REANALYSIS_SINGLE_LEVELS = (
        'reanalysis-era5-single-levels',
        era5_constants.list_predefined_variables_era5_singles_levels,
        era5_constants.list_product_type_hourly,
        Era5PredicateEra5SingleLevelsByHour)
    ERA5_REANALYSIS_SINGLE_LEVELS_MONTHLY = (
        'reanalysis-era5-single-levels-monthly-means',
        era5_constants.list_predefined_variables_era5_singles_levels,
        era5_constants.list_product_type_monthly,
        Era5PredicateEra5SingleLevelsByMonth)
    ERA5_REANALYSIS_PRESSURE_LEVELS = (
        'reanalysis-era5-pressure-levels',
        era5_constants.list_predefined_variables_era5_pressure,
        era5_constants.list_product_type_hourly,
        Era5PredicateEra5PressureLevelByHour)
    ERA5_REANALYSIS_PRESSURE_LEVELS_MONTHLY = (
        'reanalysis-era5-pressure-levels-monthly-means',
        era5_constants.list_predefined_variables_era5_pressure,
        era5_constants.list_product_type_monthly,
        Era5PredicateEra5PressureLevelsByMonth)

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._name = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, children: list = None, list_product_type=None,
                 predicate_class=None):
        self._children = children
        self._list_product_type = list_product_type
        self._predicate_class = predicate_class

    @property
    def name(self) -> str:
        return self._name

    @property
    def children(self) -> list:
        return self._children

    @property
    def list_product_type(self):
        return self._list_product_type

    @property
    def predicate_class(self):
        return self._predicate_class
