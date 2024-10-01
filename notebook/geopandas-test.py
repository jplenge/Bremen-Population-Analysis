import marimo

__generated_with = "0.8.14"
app = marimo.App(width="medium", app_title="Test geopandas")


@app.cell
def __(mo):
    import geopandas as gpd
    import pandas as pd
    import marimo as mo
    import altair as alt
    from shapely.geometry import Polygon

    return mo, pd, gpd, alt, Polygon

@app.cell
def __(gpd, pd, mo):

    df = pd.DataFrame(
        {
            "City": ["Buenos Aires", "Brasilia", "Santiago", "Bogota", "Caracas"],
            "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Venezuela"],
            "Latitude": [-34.58, -15.78, -33.45, 4.60, 10.48],
            "Longitude": [-58.66, -47.91, -70.66, -74.08, -66.86],
        }
    )

    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326"
    )

    return gdf

@app.cell
def __(gdf, alt):
    alt.Chart(geodf).mark_geoshape()

@app.cell
def __(gdf, alt, mo):
    mo.ui.altair_chart(alt.Chart(geodf).mark_geoshape())

    return

@app.cell
def __(pd, gpd, Polygon):
    df1 = pd.DataFrame({'name':['a1','a2','a3','a4','a5','a6'],
                   'loc_x':[0,1,2,3,4,5],
                   'loc_y':[1,2,3,4,5,6],
                   'grp_name':['set1','set1','set1','set2','set2','set2']})

    df1['points'] = gpd.points_from_xy(df1.loc_x, df1.loc_y)

    df1 = df1.groupby('grp_name').agg(
            name     = pd.NamedAgg(column='name',   aggfunc = lambda x: '|'.join(x)),
            geometry = pd.NamedAgg(column='points', aggfunc = lambda x: Polygon(x.values))
    ).reset_index()

    geodf = gpd.GeoDataFrame(df1, geometry='geometry')

    geodf

    return geodf



if __name__ == "__main__":
    app.run()
