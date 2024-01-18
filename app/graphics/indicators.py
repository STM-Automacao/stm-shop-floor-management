"""
Gráficos de indicadores
"""
# cSpell: words mcolors, eficiencia, vmin, vmax, cmap, figsize, linewidths, annot, cbar, xlabel,
# cSpell: words ylabel, xticks, yticks, colorscale, hoverongaps, zmin, zmax, showscale, xgap, ygap,
# cSpell: words nticks, tickmode, tickvals, ticktext, tickangle, lightgray, tickfont, showticklabels

import pandas as pd
import plotly.graph_objects as go
# pylint: disable=E0401
from helpers.types import IndicatorType


class Indicators:
    """
    Esta classe é responsável por criar os gráficos de indicadores.
    """

    def __init__(self):
        pass

    def efficiency_graphic(
        self, dataframe: pd.DataFrame, meta: int
    ) -> go.Figure:
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

        # Criar escala de cores personalizada - cores do bootstrap
        colors = [
            [0, "#dc3545"],  # danger
            [0.9, "#dc3545"],
            [0.9, "#28a745"],
            [1, "#28a745"],  # success
        ]

        # Extrair apenas o dia da data
        df_pivot.columns = pd.to_datetime(df_pivot.columns).day

        num_cells = len(df_pivot.index) * len(df_pivot.columns)
        font_size = 400 / num_cells  # Ajustar o valor 100 conforme necessário

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
                    font=dict(color="white", size=font_size),
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
            margin=dict(t=40, b=40, l=40, r=40),
        )

        return fig

    def performance_graphic(
        self, dataframe: pd.DataFrame, meta: int
    ) -> go.Figure:
        """
        Este método é responsável por criar o gráfico de performance.

        Parâmetros:
        dataframe (pd.DataFrame): DataFrame contendo os dados para o gráfico.
                                Deve incluir as colunas 'data_registro', 'turno' e 'performance'.
        meta (int): Meta de performance a ser alcançada.

        Retorna:
        fig: Objeto plotly.graph_objects.Figure com o gráfico de eficiência.

        O gráfico é um heatmap que mostra a performance média por turno e data.
        A performance é colorida de vermelho se estiver acima de 4% e
        de verde se estiver abaixo de 4%.
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
        df_pivot = df_pivot.reindex(["VES", "MAT", "NOT"])

        # Criar escala de cores personalizada - cores do bootstrap
        colors = [
            [0, "#28a745"],  # danger
            [0.04, "#28a745"],
            [0.04, "#dc3545"],
            [1, "#dc3545"],  # success
        ]

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
                    font=dict(color="white", size=8),
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
            margin=dict(t=40, b=40, l=40, r=40),
        )

        return fig

    def repair_graphic(self, dataframe: pd.DataFrame, meta: int) -> go.Figure:
        """
        Este método é responsável por criar o gráfico de reparos.

        Parâmetros:
        dataframe (pd.DataFrame): DataFrame contendo os dados para o gráfico.
                                Deve incluir as colunas 'data_registro', 'turno' e 'reparo'.
        meta (int): Meta de reparos a ser alcançada.

        Retorna:
        fig: Objeto plotly.graph_objects.Figure com o gráfico de eficiência.

        O gráfico é um heatmap que mostra a performance média por turno e data.
        A performance é colorida de vermelho se estiver acima de 4% e
        de verde se estiver abaixo de 4%.
        """

        # Converter 'data_registro' para datetime e criar uma nova coluna 'data_turno'
        dataframe["data_registro"] = pd.to_datetime(dataframe["data_registro"])
        dataframe["data_turno"] = dataframe["data_registro"].dt.strftime(
            "%Y-%m-%d"
        )

        # Agrupar por 'data_turno' e 'turno' e calcular a média da eficiência
        df_grouped = (
            dataframe.groupby(["data_turno", "turno"])["reparos"]
            .mean()
            .reset_index()
        )

        # Remodelar os dados para o formato de heatmap
        df_pivot = df_grouped.pivot(
            index="turno", columns="data_turno", values="reparos"
        )

        # Reordenar o índice do DataFrame
        df_pivot = df_pivot.reindex(["VES", "MAT", "NOT"])

        # Criar escala de cores personalizada - cores do bootstrap
        colors = [
            [0, "#28a745"],  # danger
            [0.04, "#28a745"],
            [0.04, "#dc3545"],
            [1, "#dc3545"],  # success
        ]

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
                    font=dict(color="white", size=8),
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
            margin=dict(t=40, b=40, l=40, r=40),
        )

        return fig

    @staticmethod
    def __calculate_efficiency_mean(df: pd.DataFrame) -> float:
        """
        Este método é responsável por calcular a eficiência.

        Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados para o cálculo.

        Retorna:
        efficiency (float): Eficiência calculada.
        """

        efficiency = df["eficiencia"].mean()

        return efficiency

    @staticmethod
    def __calculate_performance_mean(df: pd.DataFrame) -> float:
        """
        Este método é responsável por calcular a performance.

        Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados para o cálculo.

        Retorna:
        performance (float): Performance calculada.
        """

        performance = df["performance"].mean()

        return performance

    @staticmethod
    def __calculate_repair_mean(df: pd.DataFrame) -> float:
        """
        Este método é responsável por calcular a performance.

        Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados para o cálculo.

        Retorna:
        repair (float): Reparos calculados.
        """

        repair = df["reparos"].mean()

        return repair

    def draw_gauge_graphic(
        self, df: pd.DataFrame, ind_type: IndicatorType, meta: int
    ) -> go.Figure:
        """
        Este método é responsável por criar o gráfico de indicadores.

        Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados para o gráfico.
        ind_type (IndicatorType): Tipo de indicador.
        meta (int): Meta do indicador.

        Retorna:
        fig: Objeto plotly.graph_objects.Figure com o gráfico de indicadores.

        O gráfico é um gauge que mostra a porcentagem do indicador.
        A porcentagem é colorida de vermelho se estiver abaixo da meta e
        de verde se estiver acima da meta.
        """

        # Mapear as funções
        func_map = {
            IndicatorType.EFFICIENCY: self.__calculate_efficiency_mean,
            IndicatorType.PERFORMANCE: self.__calculate_performance_mean,
            IndicatorType.REPAIR: self.__calculate_repair_mean,
        }

        # Garantir que data_registro seja do tipo datetime
        df["data_registro"] = pd.to_datetime(df["data_registro"])

        # Verificar a primeira data_registro do dataframe para saber se os dados são do mês atual
        this_month = (
            df["data_registro"].iloc[0].month == pd.Timestamp.now().month
        )
        month = "Atual" if this_month else "Anterior"

        # Obter a função de acordo com o tipo de indicador
        func = func_map[ind_type]

        # Calcular a porcentagem
        percentage = func(df) if func is not None else 0

        # Arredondar a porcentagem
        percentage = round(percentage, 2)

        # Definir a cor de acordo com a porcentagem
        if ind_type == IndicatorType.EFFICIENCY:
            color = "#28a745" if percentage >= (meta / 100) else "#dc3545"
        else:
            color = "#dc3545" if percentage >= (meta / 100) else "#28a745"

        # Definir a escala do eixo para "performance" e "reparos"
        axis_range = (
            [0, 100] if ind_type == IndicatorType.EFFICIENCY else [40, 0]
        )

        # Criar o gráfico
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=percentage * 100,
                number={"suffix": "%"},
                domain={"x": [0, 1], "y": [0, 1]},
                title={
                    "text": month,
                    "font": {"size": 14},
                },
                gauge={
                    "axis": {
                        "range": axis_range,
                        "tickfont": {"size": 8},
                    },
                    "bar": {"color": color},
                    "steps": [
                        {"range": [0, 100], "color": "lightgray"},
                    ],
                    "threshold": {
                        "line": {"color": "black", "width": 2},
                        "thickness": 0.75,
                        "value": meta,
                    },
                },
            )
        )

        fig.update_layout(
            autosize=True,
            margin=dict(t=30, b=30, l=30, r=30),
            plot_bgcolor="white",
            height=250,
        )

        return fig

    def plot_daily_efficiency(
        self, df: pd.DataFrame, indicator: IndicatorType
    ) -> go.Figure:
        """
        Este método é responsável por criar o gráfico de linhas diária.

        Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados para o gráfico.
        indicator (IndicatorType): Tipo de indicador.

        Retorna:
        fig: Objeto plotly.graph_objects.Figure com o gráfico de linhas diária.
        """

        indicator = indicator.value

        # Converter 'data_registro' para datetime e criar uma nova coluna 'data_turno'
        df["data_registro"] = pd.to_datetime(df["data_registro"])
        df["data_turno"] = df["data_registro"].dt.strftime("%Y-%m-%d")

        # Agrupar por 'data_turno' e 'turno' e calcular a média do indicador
        df_grouped = df.groupby(["data_turno"])[indicator].mean().reset_index()

        # Multiplicar por 100 para converter para porcentagem
        df_grouped[indicator] = df_grouped[indicator] * 100

        # Criar o gráfico
        fig = go.Figure(
            go.Scatter(
                x=df_grouped["data_turno"],
                y=df_grouped[indicator],
                mode="lines+markers",
                line=dict(color="blue"),
                marker=dict(color="blue"),
                hovertemplate="<i>Dia</i>: %{x}"
                + "<br><b>Porcentagem</b>: %{y:.1f}<br>",
                hoverinfo="skip",
            )
        )

        fig.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            xaxis=dict(showticklabels=False),  # Esconde os valores dos eixos
            yaxis=dict(showticklabels=False),
            margin=dict(t=0, b=0, l=0, r=0),
            height=None,
            autosize=True,
        )

        return fig
