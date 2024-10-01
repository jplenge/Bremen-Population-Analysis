import marimo

__generated_with = "0.8.22"
app = marimo.App(width="medium", app_title="Population in Bremen")


@app.cell
def __():
    import pandas as pd
    import altair as alt
    import marimo as mo
    import geopandas as gpd
    return alt, gpd, mo, pd


@app.cell
def __(datasource_dict, mo):
    year_selection = mo.ui.dropdown(
        options=list(datasource_dict.keys()),
        value=list(datasource_dict.keys())[0],
        label="Choose year",
    )
    return (year_selection,)


@app.cell
def __(datasource_dict, pd, year_selection):
    _convert_dict = {
        "population_total": int,
        "population_male": int,
        "population_female": int,
        "german_total": int,
        "german_male": int,
        "german_female": int,
        "foreigner_total": int,
        "foreigner_male": int,
        "foreigner_female": int,
    }

    df = (
        pd.read_csv(
            datasource_dict[year_selection.value],
            encoding="ISO-8859-1",
            sep=";",
            skiprows=3,
            skipfooter=9,
            engine="python",
        )
        .rename(
            columns={
                "Unnamed: 0": "territory_key",
                "Unnamed: 1": "territorial_unit",
                "Unnamed: 2": "date",
                "Unnamed: 3": "age_group",
                "Unnamed: 4": "population_total",
                "Unnamed: 5": "population_male",
                "Unnamed: 6": "population_female",
                "zusammen": "german_total",
                "männlich": "german_male",
                "weiblich": "german_female",
                "zusammen.1": "foreigner_total",
                "männlich.1": "foreigner_male",
                "weiblich.1": "foreigner_female",
            }
        )
        .replace("x", "0")
        .astype(_convert_dict)
    )
    return (df,)


@app.cell
def __(df):
    df.info()
    return


@app.cell
def __(mo):
    mo.md("""# Population in Bremen by migration status, gender and age group""")
    return


@app.cell
def __(mo):
    territory_radio = mo.ui.radio(
        ["Stadtteil", "Ortsteil", "Stadtbezirk"],
        value="Stadtteil",
        label="Choose territorial unit",
    )
    return (territory_radio,)


@app.cell
def __(df, mo, territory_radio):
    _list = sorted(df["territorial_unit"].unique())

    territory = mo.ui.dropdown(
        options=["Stadt Bremen"]
        + list(filter(lambda k: f"{territory_radio.value}" in k, _list)),
        value="Stadt Bremen",
        label=f"Choose {territory_radio.value}",
    )
    return (territory,)


@app.cell
def __():
    datasource_dict = {
        "2023": "./data/raw/12411-03-03-2023.csv",
        "2022": "./data/raw/12411-03-03-2022.csv",    
        "2021": "./data/raw/12411-03-03-2021.csv",
        "2020": "./data/raw/12411-03-03-2020.csv",
        "2010": "./data/raw/12411-03-03-2010.csv",
        "2000": "./data/raw/12411-03-03-2000.csv",
        "1990": "./data/raw/12411-03-03-1990.csv",
        "1980": "./data/raw/12411-03-03-1980.csv",
    }


    map_feature_dict = {
        "Total population": "population_total",
        "Percentage of foreigners": "percentage_foreigner",
        "Percentage of males": "percentage_male",
        "Percentage of females": "percentage_female",
    }
    return datasource_dict, map_feature_dict


@app.cell
def __(map_feature, mo, territory, territory_radio, year_selection):
    mo.vstack(
        [
            year_selection,
            mo.hstack([territory_radio, territory, map_feature], gap=3),
        ],
        justify="start",
        align="start",
        gap=1.0,
    )
    return


@app.cell
def __(df, territory):
    df_selected = (
        df.query(f"territorial_unit == '{territory.value}'")
        .query("age_group != 'Insgesamt'")
        .assign(
            percentage_population_total=lambda x: 100
            / x["population_total"].sum()
            * x["population_total"]
        )
        .assign(
            percentage_population_male=lambda x: 100
            / x["population_male"].sum()
            * x["population_male"]
        )
        .assign(
            percentage_population_female=lambda x: 100
            / x["population_female"].sum()
            * x["population_female"]
        )
        .assign(
            percentage_german_total=lambda x: 100
            / x["german_total"].sum()
            * x["german_total"]
        )
        .assign(
            percentage_german_male=lambda x: 100
            / x["german_male"].sum()
            * x["german_male"]
        )
        .assign(
            percentage_german_female=lambda x: 100
            / x["german_female"].sum()
            * x["german_female"]
        )
        .assign(
            percentage_foreigner_total=lambda x: 100
            / x["foreigner_total"].sum()
            * x["foreigner_total"]
        )
        .assign(
            percentage_foreigner_male=lambda x: 100
            / x["foreigner_male"].sum()
            * x["foreigner_male"]
        )
        .assign(
            percentage_foreigner_female=lambda x: 100
            / x["foreigner_female"].sum()
            * x["foreigner_female"]
        )
    )

    df_selected["age_group"] = (
        df_selected["age_group"]
        .str.replace("3 - 6", "03 - 06")
        .replace("6 - 10", "06 - 10")
        .replace("unter 3", "00 - 03")
    )
    return (df_selected,)


@app.cell
def __(alt, pd):
    def generate_age_distribution_graph(
        df: pd.DataFrame,
        graph_width: int,
        yaxis_data: str,
        xaxis_data_left: str,
        xaxis_data_right: str,
        median_left: str,
        median_right: str,
        title_left: str = None,
        title_right: str = None,
    ):
        base = alt.Chart(df).properties(
            width=graph_width,
        )

        left_bar_graph = (
            base.mark_bar(color="#CFA6EA")
            .encode(
                alt.Y(yaxis_data).axis(None),
                alt.X(xaxis_data_left, title="Population").sort("descending"),
                tooltip=[
                    alt.Tooltip(yaxis_data, title="Age group"),
                    alt.Tooltip(xaxis_data_left, title="Population"),
                ],
            )
            .properties(title=title_left)
        )

        median_indicator_left = (
            alt.Chart(
                pd.DataFrame(
                    {
                        "agegroup": [median_left],
                        "color": ["red"],
                    }
                )
            )
            .mark_rule()
            .encode(y="agegroup", color=alt.Color("color:N", scale=None))
        )

        left_graph = left_bar_graph + median_indicator_left

        ###############

        right_bar_graph = (
            base.mark_bar(color="#148BE7")
            .encode(
                alt.Y(yaxis_data).axis(None),
                alt.X(xaxis_data_right, title="Population"),
                tooltip=[
                    alt.Tooltip("population_male", title="Population"),
                    alt.Tooltip("age_group", title="Age group"),
                ],
            )
            .properties(title=title_right)
        )

        median_indicator_right = (
            alt.Chart(
                pd.DataFrame(
                    {
                        "agegroup": [f"{median_right}"],
                        "color": ["red"],
                    }
                )
            )
            .mark_rule()
            .encode(y="agegroup", color=alt.Color("color:N", scale=None))
        )

        middle = (
            base.encode(
                alt.Y("age_group:N").axis(None),
                alt.Text("age_group:N"),
            )
            .mark_text(color="white")
            .properties(width=80)
        )

        right_graph = right_bar_graph + median_indicator_left

        return alt.concat(left_graph, middle, right_graph, spacing=5)


    def generate_single_age_distribution(
        df: pd.DataFrame,
        graph_width: int,
        yaxis_data: str,
        xaxis_data: str,
        median: str,
        title: str = None,
    ):
        base = alt.Chart(df).properties(
            width=graph_width,
        )

        bar_graph = (
            base.mark_bar(color="#65BFAF")
            .encode(
                alt.Y(yaxis_data).title("Age group"),
                alt.X(xaxis_data, title="Population"),
                tooltip=[
                    alt.Tooltip(yaxis_data, title="Age group"),
                    alt.Tooltip(xaxis_data, title="Population"),
                ],
            )
            .properties(title=title)
        )

        median_indicator = (
            alt.Chart(
                pd.DataFrame(
                    {
                        "age_group": [median],
                        "color": ["red"],
                    }
                )
            )
            .mark_rule()
            .encode(y="age_group", color=alt.Color("color:N", scale=None))
        )

        return bar_graph + median_indicator
    return generate_age_distribution_graph, generate_single_age_distribution


@app.cell
def __(
    df_selected,
    generate_age_distribution_graph,
    median_agegroup_bevoelkerung_m,
    median_agegroup_bevoelkerung_w,
):
    population_gender_graph = generate_age_distribution_graph(
        df=df_selected,
        graph_width=350,
        xaxis_data_left="population_female",
        xaxis_data_right="population_male",
        yaxis_data="age_group",
        title_left="Female",
        title_right="Male",
        median_left=median_agegroup_bevoelkerung_w,
        median_right=median_agegroup_bevoelkerung_m,
    )
    return (population_gender_graph,)


@app.cell
def __(
    df_selected,
    generate_single_age_distribution,
    median_agegroup_bevoelkerung,
):
    population_total_graph = generate_single_age_distribution(
        df=df_selected,
        graph_width=350,
        xaxis_data="population_total",
        yaxis_data="age_group",
        median=median_agegroup_bevoelkerung,
        title="Total population",
    )
    return (population_total_graph,)


@app.cell
def __(
    df_selected,
    generate_age_distribution_graph,
    median_agegroup_deutsch_m,
    median_agegroup_deutsch_w,
):
    german_gender_graph = generate_age_distribution_graph(
        df=df_selected,
        graph_width=350,
        xaxis_data_left="german_female",
        xaxis_data_right="german_male",
        yaxis_data="age_group",
        title_left="Female",
        title_right="Male",
        median_left=median_agegroup_deutsch_w,
        median_right=median_agegroup_deutsch_m,
    )
    return (german_gender_graph,)


@app.cell
def __(
    df_selected,
    generate_single_age_distribution,
    median_agegroup_deutsch,
):
    german_total_graph = generate_single_age_distribution(
        df=df_selected,
        graph_width=350,
        xaxis_data="german_total",
        yaxis_data="age_group",
        median=median_agegroup_deutsch,
        title="German population",
    )
    return (german_total_graph,)


@app.cell
def __(
    df_selected,
    generate_age_distribution_graph,
    median_agegroup_auslaender_m,
    median_agegroup_auslaender_w,
):
    foreigners_gender_graph = generate_age_distribution_graph(
        df=df_selected,
        graph_width=350,
        xaxis_data_left="foreigner_female",
        xaxis_data_right="foreigner_male",
        yaxis_data="age_group",
        title_left="Female",
        title_right="Male",
        median_left=median_agegroup_auslaender_w,
        median_right=median_agegroup_auslaender_m,
    )
    return (foreigners_gender_graph,)


@app.cell
def __(
    df_selected,
    generate_single_age_distribution,
    median_agegroup_auslaender,
):
    foreigners_total_graph = generate_single_age_distribution(
        df=df_selected,
        graph_width=350,
        xaxis_data="foreigner_total",
        yaxis_data="age_group",
        median=median_agegroup_auslaender,
        title="Foreign population",
    )
    return (foreigners_total_graph,)


@app.cell
def __(df_selected):
    foreigner_total_count = df_selected["foreigner_total"].sum()
    german_total_count = df_selected["german_total"].sum()
    population_total_count = df_selected["population_total"].sum()

    foreigner_female_count = df_selected["foreigner_female"].sum()
    german_female_count = df_selected["german_female"].sum()
    population_female_count = df_selected["population_female"].sum()

    foreigner_male_count = df_selected["foreigner_male"].sum()
    german_male_count = df_selected["german_male"].sum()
    population_male_count = df_selected["population_male"].sum()
    return (
        foreigner_female_count,
        foreigner_male_count,
        foreigner_total_count,
        german_female_count,
        german_male_count,
        german_total_count,
        population_female_count,
        population_male_count,
        population_total_count,
    )


@app.cell
def __(
    foreigner_female_count,
    foreigner_male_count,
    foreigner_total_count,
    german_female_count,
    german_male_count,
    german_total_count,
    mo,
    population_female_count,
    population_male_count,
    population_total_count,
):
    foreigner_total_stat = mo.stat(
        value=f"{foreigner_total_count}",
        label="Foreigner",
        caption=f"{(100/population_total_count * foreigner_total_count):.1f} %",
        bordered=True,
    )

    german_total_stat = mo.stat(
        value=f"{german_total_count}",
        label="German",
        caption=f"{(100/population_total_count * german_total_count):.1f} %",
        bordered=True,
    )

    population_total_stat = mo.stat(
        value=f"{population_total_count}",
        label="Total population",
        caption=f"{(100/population_total_count * (foreigner_total_count + german_total_count)):.1f} %",
        bordered=True,
    )

    # female

    foreigner_female_stat = mo.stat(
        value=f"{foreigner_female_count}",
        label="Foreigner (female)",
        caption=f"{(100/population_female_count * foreigner_female_count):.1f} %",
        bordered=True,
    )

    german_female_stat = mo.stat(
        value=f"{german_female_count}",
        label="German (female)",
        caption=f"{(100/population_female_count * german_female_count):.1f} %",
        bordered=True,
    )

    population_female_stat = mo.stat(
        value=f"{population_female_count}",
        label="Total population (female)",
        caption=f"{(100/population_female_count * (foreigner_female_count + german_female_count)):.1f} %",
        bordered=True,
    )

    # maennlich
    foreigner_male_stat = mo.stat(
        value=f"{foreigner_male_count}",
        label="Foreigner (male)",
        caption=f"{(100/population_male_count * foreigner_male_count):.1f} %",
        bordered=True,
    )

    german_male_stat = mo.stat(
        value=f"{german_male_count}",
        label="German (male)",
        caption=f"{(100/population_male_count * german_male_count):.1f} %",
        bordered=True,
    )

    population_male_stat = mo.stat(
        value=f"{population_male_count}",
        label="Total population (male)",
        caption=f"{(100/population_male_count * (foreigner_male_count + german_male_count)):.1f} %",
        bordered=True,
    )
    return (
        foreigner_female_stat,
        foreigner_male_stat,
        foreigner_total_stat,
        german_female_stat,
        german_male_stat,
        german_total_stat,
        population_female_stat,
        population_male_stat,
        population_total_stat,
    )


@app.cell
def __(determine_median, df_selected):
    median_agegroup_deutsch = determine_median(
        df_selected["german_total"], df_selected["age_group"]
    )

    median_agegroup_deutsch_m = determine_median(
        df_selected["german_male"], df_selected["age_group"]
    )

    median_agegroup_deutsch_w = determine_median(
        df_selected["german_female"], df_selected["age_group"]
    )

    median_agegroup_auslaender = determine_median(
        df_selected["foreigner_total"], df_selected["age_group"]
    )

    median_agegroup_auslaender_m = determine_median(
        df_selected["foreigner_male"], df_selected["age_group"]
    )

    median_agegroup_auslaender_w = determine_median(
        df_selected["foreigner_female"], df_selected["age_group"]
    )

    median_agegroup_bevoelkerung = determine_median(
        df_selected["population_total"], df_selected["age_group"]
    )

    median_agegroup_bevoelkerung_m = determine_median(
        df_selected["population_male"], df_selected["age_group"]
    )

    median_agegroup_bevoelkerung_w = determine_median(
        df_selected["population_female"], df_selected["age_group"]
    )
    return (
        median_agegroup_auslaender,
        median_agegroup_auslaender_m,
        median_agegroup_auslaender_w,
        median_agegroup_bevoelkerung,
        median_agegroup_bevoelkerung_m,
        median_agegroup_bevoelkerung_w,
        median_agegroup_deutsch,
        median_agegroup_deutsch_m,
        median_agegroup_deutsch_w,
    )


@app.cell
def stats_grid(
    foreigner_female_stat,
    foreigner_male_stat,
    foreigner_total_stat,
    german_female_stat,
    german_male_stat,
    german_total_stat,
    mo,
    population_female_stat,
    population_male_stat,
    population_total_stat,
):
    _bevoelkerung_stats_col = mo.vstack(
        [
            population_total_stat,
            population_female_stat,
            population_male_stat,
        ]
    )

    _deutsch_stats_col = mo.vstack(
        [
            german_total_stat,
            german_female_stat,
            german_male_stat,
        ]
    )

    _auslaender_stats_col = mo.vstack(
        [
            foreigner_total_stat,
            foreigner_female_stat,
            foreigner_male_stat,
        ]
    )

    stats_grid = mo.hstack(
        [_bevoelkerung_stats_col, _deutsch_stats_col, _auslaender_stats_col],
        align="start",
        justify="start",
    )
    return (stats_grid,)


@app.cell
def __(pd):
    def determine_median(population: pd.Series, agegroups: pd.Series):
        cumul_population = population.cumsum()
        half_value = cumul_population.iloc[-1] / 2

        index = (cumul_population - half_value).gt(0).idxmax()
        return agegroups.loc[index]
    return (determine_median,)


@app.cell
def graph_grid(
    foreigners_gender_graph,
    foreigners_total_graph,
    german_gender_graph,
    german_total_graph,
    mo,
    population_gender_graph,
    population_total_graph,
):
    population_col = mo.hstack(
        [
            mo.ui.altair_chart(population_total_graph),
            mo.ui.altair_chart(population_gender_graph),
        ],
        justify="start",
    )

    german_col = mo.hstack(
        [
            mo.ui.altair_chart(german_total_graph),
            mo.ui.altair_chart(german_gender_graph),
        ],
        align="center",
    )

    foreigner_col = mo.hstack(
        [
            mo.ui.altair_chart(foreigners_total_graph),
            mo.ui.altair_chart(foreigners_gender_graph),
        ],
        align="center",
    )

    population_tabs = mo.ui.tabs(
        {
            "Total population": population_col,
            "German population": german_col,
            "Foreign population": foreigner_col,
        }
    )
    return foreigner_col, german_col, population_col, population_tabs


@app.cell
def final_dashboard(map, mo, population_tabs, stats_grid):
    mo.vstack(
        [
            mo.hstack([mo.center(stats_grid), map]),
            population_tabs,
        ],
        gap=3.0,
    )
    return


@app.cell
def __(gpd, territory_radio):
    if territory_radio.value == "Stadtteil":
        gdf_ne = gpd.read_file(
            "./Verwaltungsgrenzen_HB_BHV/hb_stadtteile_BRE.shp", engine="pyogrio"
        )
    elif territory_radio.value == "Ortsteil":
        gdf_ne = gpd.read_file(
            "./Verwaltungsgrenzen_HB_BHV/hb_ortsteile_BRE.shp", engine="pyogrio"
        )
    else:
        gdf_ne = gpd.read_file(
            "./Verwaltungsgrenzen_HB_BHV/hb_stadtbezirke_BRE.shp", engine="pyogrio"
        )
    return (gdf_ne,)


@app.cell
def __(
    alt,
    gdf_ne,
    map_feature,
    map_feature_dict,
    map_info,
    mo,
    territory_radio,
):
    if territory_radio.value == "Stadtteil":
        bz = "st"
    elif territory_radio.value == "Ortsteil":
        bz = "ot"
    else:
        bz = "sb"

    _chart = (
        alt.Chart(gdf_ne)
        .mark_geoshape(stroke="green", strokeWidth=0.5)
        .project(type="identity", reflectY=True)
        .encode(
            color=alt.Color(
                f"{map_feature_dict[map_feature.value]}:Q",
                legend=alt.Legend(title=map_feature.value),
                scale=alt.Scale(type="linear"),
            ),
            tooltip=[
                alt.Tooltip(f"bez_{bz}:N", title=territory_radio.value),
                alt.Tooltip("size:Q", title="Area (qkm)", format=".2f"),
                alt.Tooltip("population_total:Q", title="Total population"),
                alt.Tooltip(
                    f"{map_feature_dict[map_feature.value]}:Q",
                    title=map_feature.value,
                    format=".2f",
                ),
            ],
        )
        .transform_lookup(
            lookup=f"bez_{bz}",
            from_=alt.LookupData(
                map_info,
                f"bez_{bz}",
                [
                    "percentage_foreigner",
                    "percentage_male",
                    "population_total",
                    "percentage_female",
                ],
            ),
        )
        .properties(title=f"{territory_radio.value}e", width=600, height=400)
    )
    map = mo.ui.altair_chart(_chart)
    return bz, map


@app.cell
def __(map_feature_dict, mo):
    map_feature = mo.ui.dropdown(
        options=list(map_feature_dict.keys()),
        value=list(map_feature_dict.keys())[0],
        label="Choose map feature",
    )
    return (map_feature,)


@app.cell
def __(df, territory_radio):
    map_info = (
        df.query(f"territorial_unit.str.contains('{territory_radio.value}')")
        .groupby(by=["territorial_unit"])
        .sum()
        .assign(
            percentage_foreigner=lambda x: 100
            / x.population_total
            * x.foreigner_total
        )
        .assign(
            percentage_male=lambda x: 100 / x.population_total * x.population_male
        )
        .assign(
            percentage_female=lambda x: 100
            / x.population_total
            * x.population_female
        )
        .reset_index()
    )

    if territory_radio.value == "Stadtteil":
        unit = "bez_st"
    elif territory_radio.value == "Ortsteil":
        unit = "bez_ot"
    else:
        unit = "bez_sb"

    map_info[unit] = (
        map_info["territorial_unit"].str.split("(").str.get(0).str.strip()
    )
    return map_info, unit


if __name__ == "__main__":
    app.run()
