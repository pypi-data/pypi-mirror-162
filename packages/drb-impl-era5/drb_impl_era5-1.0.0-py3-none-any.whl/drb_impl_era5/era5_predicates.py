from drb.exceptions import DrbException
from drb.predicat import Predicate


class Era5PredicateEra5Base(Predicate):
    def __init__(self,
                 **kwargs):

        self.arg_dict = dict(kwargs)

    def to_dict(self):
        arg_dict = {}
        for key, value in self.arg_dict.items():
            if value is not None:
                arg_dict[key] = value
        return arg_dict

    def matches(self, node) -> bool:
        return False

    @staticmethod
    def check_hour_product_type(product_type):
        if '_hour_of_day' in product_type:
            return True
        return False

    @staticmethod
    def check_hour_product_type_list(*args):
        for product_type in args:
            if Era5PredicateEra5Base.check_hour_product_type(product_type):
                return True
        return False

    def check_time_for_montly_predicate(self):
        time = self.arg_dict['time']

        if time != 0:
            if not Era5PredicateEra5Base.check_hour_product_type_list(
                    self.arg_dict['product_type']):
                raise DrbException(f'With product type to ' +
                                   self.arg_dict['product_type'] +
                                   f' time must be zero.')


class Era5PredicateEra5Land(Era5PredicateEra5Base):
    # reanalysis-era5-land
    def __init__(self,
                 year,
                 month,
                 time,
                 day,
                 area=None,
                 format='netcdf',
                 **kwargs):
        super().__init__(year=year,
                         month=month,
                         time=time,
                         area=area,
                         format=format,
                         day=day,
                         **kwargs)


class Era5PredicateEra5LandMonthly(Era5PredicateEra5Base):
    # reanalysis-era5-land-monthly-means 1950 ...
    def __init__(self,
                 year,
                 month,
                 time=0,
                 product_type='monthly_averaged_reanalysis',
                 area=None,
                 format='netcdf',
                 **kwargs):
        super().__init__(year=year,
                         month=month,
                         time=time,
                         area=area,
                         format=format,
                         product_type=product_type,
                         **kwargs)

        self.check_time_for_montly_predicate()


class Era5PredicateEra5SingleLevelsByMonth(Era5PredicateEra5Base):
    # reanalysis-era5-single-levels-monthly-means
    def __init__(self,
                 year,
                 month,
                 time=0,
                 area=None,
                 format='netcdf',
                 product_type='monthly_averaged_reanalysis',
                 **kwargs):
        super().__init__(year=year,
                         month=month,
                         time=time,
                         area=area,
                         format=format,
                         product_type=product_type,
                         **kwargs)
        self.check_time_for_montly_predicate()


class Era5PredicateEra5SingleLevelsByHour(Era5PredicateEra5Base):
    # reanalysis-era5-single-levels
    def __init__(self,
                 year,
                 month,
                 day,
                 time,
                 area=None,
                 format='netcdf',
                 product_type='reanalysis',
                 **kwargs):
        super().__init__(year=year,
                         month=month,
                         day=day,
                         time=time,
                         area=area,
                         format=format,
                         product_type=product_type,
                         **kwargs)


class Era5PredicateEra5PressureLevelsByMonth(Era5PredicateEra5Base):
    #  reanalysis-era5-pressure-levels-monthly-means
    def __init__(self,
                 year,
                 month,
                 time=0,
                 area=None,
                 pressure_level=1,
                 format='netcdf',
                 product_type='monthly_averaged_reanalysis',
                 **kwargs):
        super().__init__(year=year,
                         month=month,
                         time=time,
                         area=area,
                         pressure_level=pressure_level,
                         format=format,
                         product_type=product_type,
                         **kwargs)
        self.check_time_for_montly_predicate()


class Era5PredicateEra5PressureLevelByHour(Era5PredicateEra5Base):
    # reanalysis-era5-pressure-levels
    def __init__(self,
                 year,
                 month,
                 day,
                 time,
                 area=None,
                 pressure_level=1,
                 format='netcdf',
                 product_type='reanalysis',
                 **kwargs):
        super().__init__(year=year,
                         month=month,
                         day=day,
                         time=time,
                         area=area,
                         pressure_level=pressure_level,
                         format=format,
                         product_type=product_type,
                         **kwargs)
