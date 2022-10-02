import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from typing import Optional, List


@st.cache
def load_data() -> pd.DataFrame:
    return pd.read_csv("SwarmResults.csv", sep=";", decimal=".")


def main() -> None:
    st.title("Adaptive Swarm Utilization")
    data: pd.DataFrame = load_data()

    group_size: Optional[int] = st.radio(
        "Group size",
        [1, 5, 20],
        index=0,
        help="How many friendly targets (including player) should be simulated",
        horizontal=True,
        label_visibility="visible",
    )
    enemy_count: int = st.slider(
        "Enemy count",
        min_value=1,
        max_value=10,
        value=1,
        step=1,
        help="How many enemies should be simulated",
    )
    has_swarm: Optional[bool] = st.radio(
        "Has Circle of Life and Death talented",
        [False, True],
        index=0,
        help="Is the talent Circle of Life and Death selected",
        horizontal=True,
        label_visibility="visible",
    )

    strategies: List[str] = st.multiselect(
        "Strategies",
        ["All"] + list(data.stratName.unique()),
        default="All",
        help="What swarm cast strategies should be simulated",
        label_visibility="visible",
    )

    ticks_per_second: bool = st.checkbox("All ticks per second", value=True)
    friendly_ticks_per_second: bool = st.checkbox(
        "Friendly ticks per second", value=True
    )
    enemy_ticks_per_second: bool = st.checkbox("Enemy ticks per second", value=True)

    if "All" in strategies:
        strat_sel = [True] * data.shape[0]
    else:
        strat_sel = data.stratName.isin(strategies)
    filtered_data: pd.DataFrame = data.loc[
        (data.group_size == group_size)
        & (data.enemyCount == enemy_count)
        & (data.hasCircle == has_swarm)
        & strat_sel
    ]

    tps: pd.DataFrame = filtered_data.loc[:, ["stratName", "ticksPerSecond"]]
    tps["type"] = "all ticks"
    tps.columns = ["stratName", "ticksPerSecond", "type"]
    ftps: pd.DataFrame = filtered_data.loc[:, ["stratName", "friendlyTicksPerTime"]]
    ftps["type"] = "friendly ticks"
    ftps.columns = ["stratName", "ticksPerSecond", "type"]
    etps: pd.DataFrame = filtered_data.loc[:, ["stratName", "enemyTicksPerTime"]]
    etps["type"] = "enemy ticks"
    etps.columns = ["stratName", "ticksPerSecond", "type"]
    plot_dfs = []
    if ticks_per_second:
        plot_dfs += [tps]
    if friendly_ticks_per_second:
        plot_dfs += [ftps]
    if enemy_ticks_per_second:
        plot_dfs += [etps]
    if len(plot_dfs) > 0 and len(strategies) > 0:
        plot_df = pd.concat(plot_dfs, axis=0)

        if len(plot_dfs) == 1:
            colors = []
            for strat in plot_df.stratName.unique():
                if "enemyfirst" in strat.lower():
                    colors.append("#ff8800")
                elif "friendly" in strat.lower():
                    colors.append("#66cc66")
                elif "enemy" in strat.lower():
                    colors.append("#ff6666")
                else:
                    colors.append("#6666ff")
            ax = sns.barplot(
                y="stratName",
                x="ticksPerSecond",
                data=plot_df,
                orient="h",
                palette=colors,
            )
        else:
            ax = sns.barplot(
                y="stratName",
                x="ticksPerSecond",
                hue="type",
                data=plot_df,
                orient="h",
            )
            sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
        fig = plt.gcf()
        # fig.patch.set_facecolor("blue")
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.tick_params(colors="white", which="both")

        # print(type(fig))

        st.pyplot(plt.gcf())
    else:
        st.text("Select at least one tick type and strategy")

    st.subheader("Filtered data")
    st.write(filtered_data)

    st.subheader("Raw data")
    st.write(data)


if __name__ == "__main__":
    main()
