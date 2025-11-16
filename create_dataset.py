import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# varables
name_pref = "befolkning_1km_"
directory = "data/geoparquet/"
start_year = 2015
end_year = 2024

#define the demographic ages
kids_cols = ['ald0_5', 'ald5_10', 'ald10_15', 'ald15_20']
adult_cols = ['ald20_25','ald25_30', 'ald30_35', 'ald35_40', 'ald40_45', 'ald45_50',
       'ald50_55', 'ald55_60', 'ald60_65']
senior_cols = ['ald65_70', 'ald70_75', 'ald75_80', 'ald80_85', 'ald85_90', 'ald90_95', 'ald95_100', 'ald100w']

# columns to sum during aggregation
SUM_COLUMNS = ['rutstorl','beftotalt','ald0_5', 'ald5_10', 'ald10_15', 'ald15_20',
       'ald20_25', 'ald25_30', 'ald30_35', 'ald35_40', 'ald40_45', 'ald45_50',
       'ald50_55', 'ald55_60', 'ald60_65', 'ald65_70', 'ald70_75', 'ald75_80',
       'ald80_85', 'ald85_90', 'ald90_95', 'ald95_100', 'ald100w']
DROP_COLUMNS = ['rutid_inspire', 'rutid_scb', 'geometry', 'lanskod', 'regsonamn','referenstid','version','kvinna','man']

def main():
    # import regSO geoparquet
    regSO = gpd.read_parquet(directory + "RegSO_2025_Link.parquet")
    #drop geometry column to avoid issues during merge
    regSO = regSO.drop(columns="geometry")

    # loop through years to concatenate data keeping all years in a single geodataframe without merging with regso
    for year in range(start_year, end_year + 1):
        # import geoparquet for the year
        gdf_year = gpd.read_parquet(directory + name_pref + str(year) + ".parquet")
        # add year column
        gdf_year["year"] = year
        
        # concatenate to regSO
        if year == start_year:
            gdf_all_years = gdf_year
        else:
            gdf_all_years = pd.concat([gdf_all_years, gdf_year], ignore_index=True)

    # add all RegSO data to the concatenated geodataframe based in rutid_inspire column
    gdf_all_years = gdf_all_years.merge(regSO, on="rutid_inspire", how="left")
    gdf_all_years = gdf_all_years.to_crs(epsg=3006)
    gdf_all_years = gdf_all_years.dropna()

    #drop unnecesary columns
    gdf_all_years = gdf_all_years.drop(columns=DROP_COLUMNS)

    #create a aggregation based on regsonamnskod and year columns and then divide all the summed columns by summing up the rutstorl column to get population density per region and year
    gdf_aggregated = gdf_all_years.groupby(['regsokod', 'year'])[SUM_COLUMNS].sum().reset_index()
    for col in SUM_COLUMNS:
        if col != 'rutstorl':
            gdf_aggregated[col] = gdf_aggregated[col] / (gdf_aggregated['rutstorl'] / 1000)

    #the same for komnamnskod
    gdf_aggregated_kom = gdf_all_years.groupby(['kommunkod', 'year'])[SUM_COLUMNS].sum().reset_index()
    for col in SUM_COLUMNS:
        if col != 'rutstorl':
            gdf_aggregated_kom[col] = gdf_aggregated_kom[col] / (gdf_aggregated_kom['rutstorl'] / 1000)

    gdf_with_kommun = gdf_all_years.merge(gdf_aggregated_kom, on=['kommunkod', 'year'], suffixes=('', '_kommun_sum'), how='left')
    gdf_with_all = gdf_with_kommun.merge(gdf_aggregated, on=['regsokod', 'year'], suffixes=('', '_regso_sum'), how='left')

    #summing up the population for each demographic per year and then removing the original columns
    gdf_with_all['kids_population'] = gdf_with_all[kids_cols].sum(axis=1)
    gdf_with_all['adult_population'] = gdf_with_all[adult_cols].sum(axis=1)
    gdf_with_all['senior_population'] = gdf_with_all[senior_cols].sum(axis=1)

    #doing the same with the kommun and regso summed columns
    gdf_with_all['kids_population_kommun_sum'] = gdf_with_all[[col + '_kommun_sum' for col in kids_cols]].sum(axis=1)
    gdf_with_all['adult_population_kommun_sum'] = gdf_with_all[[col + '_kommun_sum' for col in adult_cols]].sum(axis=1)
    gdf_with_all['senior_population_kommun_sum'] = gdf_with_all[[col + '_kommun_sum' for col in senior_cols]].sum(axis=1)
    gdf_with_all['kids_population_regso_sum'] = gdf_with_all[[col + '_regso_sum' for col in kids_cols]].sum(axis=1)
    gdf_with_all['adult_population_regso_sum'] = gdf_with_all[[col + '_regso_sum' for col in adult_cols]].sum(axis=1)
    gdf_with_all['senior_population_regso_sum'] = gdf_with_all[[col + '_regso_sum' for col in senior_cols]].sum(axis=1)

    #dropping the original columns
    agedrop_cols = kids_cols + adult_cols + senior_cols + [col + '_kommun_sum' for col in kids_cols + adult_cols + senior_cols] + [col + '_regso_sum' for col in kids_cols + adult_cols + senior_cols]
    gdf_with_all = gdf_with_all.drop(columns=agedrop_cols)

    #export to geoparquet
    gdf_with_all.to_parquet(directory + "befolkning_1km_2015_2024_regso_kommun_aggregated.parquet")
    print("Dataset created and saved to " + directory + "befolkning_1km_2015_2024_regso_kommun_aggregated.parquet")

if __name__ == "__main__":
    main()
