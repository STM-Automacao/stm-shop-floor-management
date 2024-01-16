"""
Gráficos de indicadores
"""
# cSpell: words mcolors, eficiencia, vmin, vmax, cmap, figsize, linewidths, annot, cbar, xlabel,
# cSpell: words ylabel, xticks, yticks, colorscale, hoverongaps, zmin, zmax, showscale, xgap, ygap,
# cSpell: words nticks, tickmode, tickvals, ticktext, tickangle

import os

import matplotlib
import pandas as pd
import plotly.graph_objects as go

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
        fig: Objeto plotly.graph_objects.Figure com o gráfico de eficiência.

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
        df_pivot = df_pivot.reindex(["VES", "MAT", "NOT"])

        # Criar escala de cores personalizada
        colors = [[0, "red"], [0.9, "red"], [0.9, "green"], [1, "green"]]

        # Extrair apenas o dia da data
        df_pivot.columns = pd.to_datetime(df_pivot.columns).day

        # Criar o gráfico de calor
        fig = go.Figure(
            data=go.Heatmap(
                z=df_pivot.values,
                x=df_pivot.columns,
                y=df_pivot.index,
                colorscale=colors,
                zmin=0,
                zmax=1,  # Escala de valores de 0 a 1
                hoverongaps=False,
                hovertemplate="Turno: %{y}<br>Dia: %{x}<br>Valor: %{z:.1%}",
                showscale=False,  # Não mostrar a escala de cores
                xgap=1,  # Espaçamento entre os dias
                ygap=1,  # Espaçamento entre os turnos
            )
        )

        # Adicionar anotações com a média da eficiência
        # pylint: disable=consider-using-enumerate
        for i in range(len(df_pivot.index)):
            for j in range(len(df_pivot.columns)):
                fig.add_annotation(
                    x=df_pivot.columns[j],
                    y=df_pivot.index[i],
                    text=f"{df_pivot.values[i, j]:.1%}",
                    showarrow=False,
                    font=dict(color="white"),
                )

        # Definir o título do gráfico
        fig.update_layout(
            title=f"Eficiência - Meta {meta}%",
            xaxis_title="Dia",
            yaxis_title="Turno",
            title_x=0.5,  # Centralizar o título
            xaxis_nticks=31,  # Definir o número de dias
            xaxis=dict(
                tickmode="linear",
                tickvals=list(range(1, 32)),  # Definir os dias
                ticktext=list(range(1, 32)),  # Definir os dias
                tickangle=45,  # Rotacionar os dias
            ),
            yaxis=dict(
                tickmode="linear",
                tickangle=45,
            ),
            plot_bgcolor="white",
        )

        return fig

    def performance_graphic(self, dataframe: pd.DataFrame, meta: int):
        """
        Este método é responsável por criar o gráfico de performance.

        Parâmetros:
        dataframe (pd.DataFrame): DataFrame contendo os dados para o gráfico.
                                Deve incluir as colunas 'data_registro', 'turno' e 'performance'.
        meta (int): Meta de performance a ser alcançada.

        Retorna:
        fig: Objeto plotly.graph_objects.Figure com o gráfico de eficiência.

        O gráfico é um heatmap que mostra a performance média por turno e data.
        A performance é colorida de vermelho se estiver abaixo de 4% e
        de verde se estiver acima de 4%.
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

        # Criar escala de cores personalizada
        colors = [[0, "green"], [0.04, "green"], [0.04, "red"], [1, "red"]]

        # Extrair apenas o dia da data
        df_pivot.columns = pd.to_datetime(df_pivot.columns).day

        # Criar o gráfico de calor
        fig = go.Figure(
            data=go.Heatmap(
                z=df_pivot.values,
                x=df_pivot.columns,
                y=df_pivot.index,
                colorscale=colors,
                zmin=0,
                zmax=1,  # Escala de valores de 0 a 1
                hoverongaps=False,
                hovertemplate="Turno: %{y}<br>Dia: %{x}<br>Valor: %{z:.1%}",
                showscale=False,  # Não mostrar a escala de cores
                xgap=1,  # Espaçamento entre os dias
                ygap=1,  # Espaçamento entre os turnos
            )
        )

        # Adicionar anotações com a média da eficiência
        # pylint: disable=consider-using-enumerate
        for i in range(len(df_pivot.index)):
            for j in range(len(df_pivot.columns)):
                fig.add_annotation(
                    x=df_pivot.columns[j],
                    y=df_pivot.index[i],
                    text=f"{df_pivot.values[i, j]:.1%}",
                    showarrow=False,
                    font=dict(color="white"),
                )

        # Definir o título do gráfico
        fig.update_layout(
            title=f"Performance - Meta {meta}%",
            xaxis_title="Dia",
            yaxis_title="Turno",
            title_x=0.5,  # Centralizar o título
            xaxis_nticks=31,  # Definir o número de dias
            xaxis=dict(
                tickmode="linear",
                tickvals=list(range(1, 32)),  # Definir os dias
                ticktext=list(range(1, 32)),  # Definir os dias
                tickangle=45,  # Rotacionar os dias
            ),
            yaxis=dict(
                tickmode="linear",
                tickangle=45,
            ),
            plot_bgcolor="white",
        )

        return fig

    def repair_graphic(self, dataframe: pd.DataFrame, meta: int):
        """
        Este método é responsável por criar o gráfico de reparos.

        Parâmetros:
        dataframe (pd.DataFrame): DataFrame contendo os dados para o gráfico.
                                Deve incluir as colunas 'data_registro', 'turno' e 'reparo'.
        meta (int): Meta de reparos a ser alcançada.

        Retorna:
        fig: Objeto plotly.graph_objects.Figure com o gráfico de eficiência.

        O gráfico é um heatmap que mostra a performance média por turno e data.
        A performance é colorida de vermelho se estiver abaixo de 4% e
        de verde se estiver acima de 4%.
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

        # Criar escala de cores personalizada
        colors = [[0, "green"], [0.04, "green"], [0.04, "red"], [1, "red"]]

        # Extrair apenas o dia da data
        df_pivot.columns = pd.to_datetime(df_pivot.columns).day

        # Criar o gráfico de calor
        fig = go.Figure(
            data=go.Heatmap(
                z=df_pivot.values,
                x=df_pivot.columns,
                y=df_pivot.index,
                colorscale=colors,
                zmin=0,
                zmax=1,  # Escala de valores de 0 a 1
                hoverongaps=False,
                hovertemplate="Turno: %{y}<br>Dia: %{x}<br>Valor: %{z:.1%}",
                showscale=False,  # Não mostrar a escala de cores
                xgap=1,  # Espaçamento entre os dias
                ygap=1,  # Espaçamento entre os turnos
            )
        )

        # Adicionar anotações com a média da eficiência
        # pylint: disable=consider-using-enumerate
        for i in range(len(df_pivot.index)):
            for j in range(len(df_pivot.columns)):
                fig.add_annotation(
                    x=df_pivot.columns[j],
                    y=df_pivot.index[i],
                    text=f"{df_pivot.values[i, j]:.1%}",
                    showarrow=False,
                    font=dict(color="white"),
                )

        # Definir o título do gráfico
        fig.update_layout(
            title=f"Reparos - Meta {meta}%",
            xaxis_title="Dia",
            yaxis_title="Turno",
            title_x=0.5,  # Centralizar o título
            xaxis_nticks=31,  # Definir o número de dias
            xaxis=dict(
                tickmode="linear",
                tickvals=list(range(1, 32)),  # Definir os dias
                ticktext=list(range(1, 32)),  # Definir os dias
                tickangle=45,  # Rotacionar os dias
            ),
            yaxis=dict(
                tickmode="linear",
                tickangle=45,
            ),
            plot_bgcolor="white",
        )

        return fig
