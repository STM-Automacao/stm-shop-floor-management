"""
Gráficos de indicadores por turno.
"""
# cSpell: words mcolors, eficiencia, vmin, vmax, cmap, figsize, linewidths, annot, cbar, xlabel,
# cSpell: words ylabel, xticks, yticks, colorscale, hoverongaps, zmin, zmax, showscale, xgap, ygap,
# cSpell: words nticks, tickmode, tickvals, ticktext, tickangle, lightgray, tickfont, showticklabels
# cSpell: words ndenumerate producao_total customdata xaxes

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# pylint: disable=E0401
# from helpers.types import IndicatorType


class IndicatorsTurn:
    """
    Esta classe é responsável por criar os gráficos de indicadores.
    """

    def __init__(self):
        self.danger_color = "#dc3545"
        self.warning_color = "#ffc107"
        self.success_color = "#198754"

    def get_eff_heat_turn(
        self,
        dataframe: pd.DataFrame,
        meta: int = 90,
        annotations: bool = False,
    ) -> go.Figure:
        """
        Este método é responsável por criar o gráfico de eficiência, por turno.

        Parâmetros:
        dataframe (pd.DataFrame): DataFrame contendo os dados para o gráfico.
                                Deve incluir as colunas 'data_registro', 'turno' e 'eficiencia'.
        meta (int): Meta de eficiência a ser alcançada. Padrão: 90.
        annotations (bool): Se True, adiciona anotações com a média da eficiência.

        Retorna:
        fig: Objeto plotly.graph_objects.Figure com o gráfico de eficiência.

        O gráfico é um heatmap que mostra a eficiência média por maquina e data.
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
            dataframe.groupby(["data_turno", "linha"])["eficiencia"]
            .mean()
            .reset_index()
        )

        # Ordenar por linha e data
        df_grouped = df_grouped.sort_values(
            ["linha", "data_turno"], ascending=[True, True]
        )

        # Remodelar os dados para o formato de heatmap
        df_pivot = df_grouped.pivot(
            index="linha", columns="data_turno", values="eficiencia"
        )

        # Criar escala de cores personalizada - cores do bootstrap
        colors = [
            [0, self.danger_color],
            [0.9, self.danger_color],
            [0.9, self.success_color],
            [1, self.success_color],
        ]

        # Extrair apenas o dia da data
        df_pivot.columns = pd.to_datetime(df_pivot.columns).day

        num_cells = len(df_pivot.index) * len(df_pivot.columns)
        font_size = 3000 / num_cells

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
                hovertemplate="Linha: %{y}<br>Dia: %{x}<br>Eficiência: %{z:.1%}",
                showscale=False,  # Não mostrar a escala de cores
                xgap=1,  # Espaçamento entre os dias
                ygap=1,  # Espaçamento entre os turnos
            )
        )

        # Adicionar anotações com a média da eficiência
        if annotations:
            for (i, j), value in np.ndenumerate(df_pivot.values):
                fig.add_annotation(
                    x=df_pivot.columns[j],
                    y=df_pivot.index[i],
                    text=f"{value:.1%}",
                    showarrow=False,
                    font=dict(color="white", size=font_size),
                )

        # Definir o título do gráfico
        fig.update_layout(
            title=f"Eficiência - Meta {meta}%",
            xaxis_title="Dia",
            yaxis_title="Linha",
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

    def get_eff_bar_turn(
        self, dataframe: pd.DataFrame, meta: int = 90
    ) -> go.Figure:
        """
        Este método é responsável por criar o gráfico de eficiência, por turno.

        Parâmetros:
        dataframe (pd.DataFrame): DataFrame contendo os dados para o gráfico.
                                Deve incluir as colunas 'linha', 'turno',
                                'producao_total e 'eficiencia'.
        meta (int): Meta de eficiência a ser alcançada. Padrão: 90.

        Retorna:
        fig: Objeto plotly.graph_objects.Figure com o gráfico de eficiência.
        """

        # Agrupar por 'turno' e "linha" e calcular a média da eficiência e soma da produção
        df_grouped = (
            dataframe.groupby(["linha", "turno"])
            .agg({"eficiencia": "mean", "producao_total": "sum"})
            .reset_index()
        )

        # Ajustar produção total para caixas, dividindo por 10
        df_grouped["producao_total"] = (
            df_grouped["producao_total"] / 10
        ).round(0)

        # Gráfico de barras
        fig = px.bar(
            df_grouped,
            orientation="h",
            x="eficiencia",
            y="linha",
            color="turno",
            barmode="group",
            hover_data={
                "producao_total": True,
                "linha": False,
                "eficiencia": False,
            },
            color_discrete_map={
                "NOT": self.danger_color,
                "MAT": self.warning_color,
                "VES": self.success_color,
            },
            labels={"eficiencia": "Eficiência"},
        )

        # Ajustar hover
        fig.update_traces(
            hovertemplate="<b>Linha</b>: %{y}<br>"
            "<b>Eficiência</b>: %{x:.1%}<br>"
            "<b>Produção</b>: %{customdata[0]} caixas<br>",
        )

        # Definir o título do gráfico
        fig.update_layout(
            title="Eficiência por Linhas",
            xaxis_title="Eficiência",
            yaxis_title="Linha",
            title_x=0.5,  # Centralizar o título
            plot_bgcolor="white",
            margin=dict(t=40, b=40, l=40, r=40),
            legend=dict(
                title_text="Turno",
            ),
        )

        # Ajustar valores de x para porcentagem
        fig.update_xaxes(tickformat=".0%")

        # Calcular a média geral de eficiência
        avg_efficiency = df_grouped["eficiencia"].mean()

        # Adicionar linha de média geral
        fig.add_trace(
            go.Scatter(
                x=[avg_efficiency] * len(df_grouped["linha"]),
                y=df_grouped["linha"],
                mode="lines",
                name="Média Geral",
                line=dict(dash="dash", color="black"),
                hovertemplate="<b>Média Geral</b>: %{x:.1%}<br>",
            )
        )

        # Adicionar linha de meta
        fig.add_trace(
            go.Scatter(
                x=[meta / 100] * len(df_grouped["linha"]),
                y=df_grouped["linha"],
                mode="lines",
                name="Meta",
                line=dict(dash="dash", color="red"),
                hovertemplate="<b>Meta</b>: %{x:.1%}<br>",
            )
        )

        return fig
