list_predefined_variables_era5_land = [
    '10m_u_component_of_wind',
    '10m_v_component_of_wind',
    '2m_dewpoint_temperature',
    '2m_temperature',
    'significant_height_of_combined_wind_waves_and_swell',
    'surface_pressure',
    'total_precipitation']

list_predefined_variables_era5_singles_levels_plus = [
    'mean_sea_level_pressure',
    'mean_wave_direction',
    'mean_wave_period',
    'sea_surface_temperature',
    'significant_height_of_combined_wind_waves_and_swell']

list_predefined_variables_era5_pressure = [
    'divergence', 'fraction_of_cloud_cover', 'geopotential',
    'ozone_mass_mixing_ratio', 'potential_vorticity', 'relative_humidity',
    'specific_cloud_ice_water_content',
    'specific_cloud_liquid_water_content', 'specific_humidity',
    'specific_rain_water_content', 'specific_snow_water_content',
    'temperature',
    'u_component_of_wind', 'v_component_of_wind', 'vertical_velocity',
    'vorticity'
]

list_predefined_variables_era5_singles_levels = \
    list_predefined_variables_era5_land + \
    list_predefined_variables_era5_singles_levels_plus

list_product_type_hourly = ['ensemble_mean', 'ensemble_members',
                            'ensemble_spread', 'reanalysis']

list_product_type_monthly = [
    'monthly_averaged_ensemble_members',
    'monthly_averaged_ensemble_members_by_hour_of_day',
    'monthly_averaged_reanalysis',
    'monthly_averaged_reanalysis_by_hour_of_day']

list_product_type_land_monthly = [
    'monthly_averaged_reanalysis',
    'monthly_averaged_reanalysis_by_hour_of_day']
