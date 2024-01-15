"""
Gráficos de indicadores
"""
# cSpell: words mcolors, eficiencia, vmin, vmax, cmap, figsize, linewidths, annot, cbar, xlabel,
# cSpell: words ylabel, xticks, yticks

import os

import matplotlib
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import plotly.tools as tls
import seaborn as sns

matplotlib.use("Agg")

script_dir = os.path.dirname(
    os.path.abspath(__file__)
)  # <-- absolute dir the script is in
file_path = os.path.join(
    script_dir, "../assets/"
)  # <-- absolute dir the script is in


class Indicators:
    """
    Esta classe é responsável por criar os gráficos de indicadores.
    """

    def __init__(self):
        pass

    def efficiency_graphic(self, dataframe: pd.DataFrame, meta: int):
        """
        Este método é responsável por criar o gráfico de eficiência.

        Parâmetros:
        dataframe (pd.DataFrame): DataFrame contendo os dados para o gráfico.
                                Deve incluir as colunas 'data_registro', 'turno' e 'eficiencia'.
        meta (int): Meta de eficiência a ser alcançada.

        Retorna:
        plt: Objeto matplotlib.pyplot com o gráfico de eficiência.

        O gráfico é um heatmap que mostra a eficiência média por turno e data.
        A eficiência é colorida de vermelho se estiver abaixo de 90% e
        de verde se estiver acima de 90%.
        """

        # Converter 'data_registro' para datetime e criar uma nova coluna 'data_turno'
        dataframe["data_registro"] = pd.to_datetime(dataframe["data_registro"])
        dataframe["data_turno"] = dataframe["data_registro"].dt.strftime(
            "%Y-%m-%d"
        )

        # Agrupar por 'data_turno' e 'turno' e calcular a média da eficiência
        df_grouped = (
            dataframe.groupby(["data_turno", "turno"])["eficiencia"]
            .mean()
            .reset_index()
        )

        # Remodelar os dados para o formato de heatmap
        df_pivot = df_grouped.pivot(
            index="turno", columns="data_turno", values="eficiencia"
        )

        # Reordenar o índice do DataFrame
        df_pivot = df_pivot.reindex(["NOT", "MAT", "VES"])

        # Definir as cores baseado na eficiência
        colors = ["red", "red", "green", "green"]
        vmin, vmax = 0, 1  # Definir o intervalo de cores de 0 a 1
        norm = plt.Normalize(vmin, vmax)
        nodes = [
            vmin,
            0.89,
            0.9,
            vmax,
        ]  # Definir o ponto de mudança de cor para 90%
        cmap = mcolors.LinearSegmentedColormap.from_list(
            "", list(zip(nodes, colors))
        )

        # Criar o gráfico de calor
        plt.figure(figsize=(15, 5))
        sns.heatmap(
            df_pivot,
            cmap=cmap,
            norm=norm,
            linewidths=0.5,
            annot=True,
            fmt=".1%",
            cbar=False,
        )
        plt.title(f"Eficiência - Meta {meta}%")
        plt.xlabel("Data")
        plt.ylabel("Turno")

        # Definir os rótulos do eixo x para os dias e rotacionar 45 graus
        days = [date[-2:] for date in df_pivot.columns]
        plt.xticks(ticks=plt.xticks()[0], labels=days, rotation=45)

        # Rotacionar os rótulos do eixo y
        plt.yticks(rotation=45)

        # Remover os ticks dos eixos x e y
        plt.gca().tick_params(axis="both", which="both", length=0)

        # plt.show()

        plotly_fig = tls.mpl_to_plotly(plt.gcf())

        return go.Figure(plotly_fig)

    def performance_graphic(self, dataframe: pd.DataFrame, meta: int):
        """
        Este método é responsável por criar o gráfico de performance.
        """

        # Converter 'data_registro' para datetime e criar uma nova coluna 'data_turno'
        dataframe["data_registro"] = pd.to_datetime(dataframe["data_registro"])
        dataframe["data_turno"] = dataframe["data_registro"].dt.strftime(
            "%Y-%m-%d"
        )

        # Agrupar por 'data_turno' e 'turno' e calcular a média da eficiência
        df_grouped = (
            dataframe.groupby(["data_turno", "turno"])["performance"]
            .mean()
            .reset_index()
        )

        # Remodelar os dados para o formato de heatmap
        df_pivot = df_grouped.pivot(
            index="turno", columns="data_turno", values="performance"
        )

        # Reordenar o índice do DataFrame
        df_pivot = df_pivot.reindex(["NOT", "MAT", "VES"])

        # Definir as cores baseado na eficiência
        colors = ["green", "green", "red", "red"]
        vmin, vmax = 0, 1  # Definir o intervalo de cores de 0 a 1
        norm = plt.Normalize(vmin, vmax)
        nodes = [
            vmin,
            0.04,
            0.041,
            vmax,
        ]  # Definir o ponto de mudança de cor para 4%
        cmap = mcolors.LinearSegmentedColormap.from_list(
            "", list(zip(nodes, colors))
        )

        # Criar o gráfico de calor
        plt.figure(figsize=(15, 5))
        sns.heatmap(
            df_pivot,
            cmap=cmap,
            norm=norm,
            linewidths=0.5,
            annot=True,
            fmt=".1%",
            cbar=False,
        )
        plt.title(f"Performance - Meta {meta}%")
        plt.xlabel("Data")
        plt.ylabel("Turno")

        # Definir os rótulos do eixo x para os dias e rotacionar 45 graus
        days = [date[-2:] for date in df_pivot.columns]
        plt.xticks(ticks=plt.xticks()[0], labels=days, rotation=45)

        # Rotacionar os rótulos do eixo y
        plt.yticks(rotation=45)

        # Remover os ticks dos eixos x e y
        plt.gca().tick_params(axis="both", which="both", length=0)

        # plt.show()
        return plt

    def reparos_graphic(self, dataframe: pd.DataFrame, meta: int):
        """
        Este método é responsável por criar o gráfico de reparos.
        """

        # Converter 'data_registro' para datetime e criar uma nova coluna 'data_turno'
        dataframe["data_registro"] = pd.to_datetime(dataframe["data_registro"])
        dataframe["data_turno"] = dataframe["data_registro"].dt.strftime(
            "%Y-%m-%d"
        )

        # Agrupar por 'data_turno' e 'turno' e calcular a média da eficiência
        df_grouped = (
            dataframe.groupby(["data_turno", "turno"])["reparo"]
            .mean()
            .reset_index()
        )

        # Remodelar os dados para o formato de heatmap
        df_pivot = df_grouped.pivot(
            index="turno", columns="data_turno", values="reparo"
        )

        # Reordenar o índice do DataFrame
        df_pivot = df_pivot.reindex(["NOT", "MAT", "VES"])

        # Definir as cores baseado na eficiência
        colors = ["green", "green", "red", "red"]
        vmin, vmax = 0, 1  # Definir o intervalo de cores de 0 a 1
        norm = plt.Normalize(vmin, vmax)
        nodes = [
            vmin,
            0.04,
            0.041,
            vmax,
        ]  # Definir o ponto de mudança de cor para 4%
        cmap = mcolors.LinearSegmentedColormap.from_list(
            "", list(zip(nodes, colors))
        )

        # Criar o gráfico de calor
        plt.figure(figsize=(15, 5))
        sns.heatmap(
            df_pivot,
            cmap=cmap,
            norm=norm,
            linewidths=0.5,
            annot=True,
            fmt=".1%",
            cbar=False,
        )
        plt.title(f"Reparos - Meta {meta}%")
        plt.xlabel("Data")
        plt.ylabel("Turno")

        # Definir os rótulos do eixo x para os dias e rotacionar 45 graus
        days = [date[-2:] for date in df_pivot.columns]
        plt.xticks(ticks=plt.xticks()[0], labels=days, rotation=45)

        # Rotacionar os rótulos do eixo y
        plt.yticks(rotation=45)

        # Remover os ticks dos eixos x e y
        plt.gca().tick_params(axis="both", which="both", length=0)

        # plt.show()
        return plt
