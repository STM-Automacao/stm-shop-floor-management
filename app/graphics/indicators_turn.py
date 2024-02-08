"""
Autor: Bruno Tomaz
Data: 23/01/2024
Módulo responsável por criar os gráficos de indicadores por turno.
"""

# cSpell: words mcolors, eficiencia, vmin, vmax, cmap, figsize, linewidths, annot, cbar, xlabel,
# cSpell: words ylabel, xticks, yticks, colorscale, hoverongaps, zmin, zmax, showscale, xgap, ygap,
# cSpell: words nticks, tickmode, tickvals, ticktext, tickangle, lightgray, tickfont, showticklabels
# cSpell: words ndenumerate producao_total customdata xaxes usuario traceorder yref bordercolor
# cSpell: words borderwidth borderpad ticksuffix sabado solucao viridis categoryorder aggfunc


import matplotlib.colors as mcolors
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

# pylint: disable=E0401
from helpers.types import BSColorsEnum, IndicatorType
from service.times_data import TimesData


class IndicatorsTurn:
    """
    Esta classe é responsável por criar os gráficos de indicadores.
    """

    def __init__(self):
        self.danger_color = "#e30613"
        self.success_color = "#00a13a"
        self.warning_color = "#ffdd00"
        self.grey_500_color = "#adb5bd"
        self.grey_600_color = "#6c757d"
        self.grey_700_color = "#495057"
        self.grey_800_color = "#343a40"
        self.grey_900_color = "#212529"
        self.times_data = TimesData()

    def get_eff_heat_turn(
        self,
        df_pivot: pd.DataFrame,
        annotations: list,
        meta: int = 90,
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

        # Criar escala de cores personalizada - cores do bootstrap
        colors = [
            [0, self.danger_color],
            [0.9, self.danger_color],
            [0.9, self.success_color],
            [1, self.success_color],
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
                hovertemplate="Linha: %{y}<br>Dia: %{x}<br>Eficiência: %{z:.1%}",
                showscale=False,  # Não mostrar a escala de cores
                xgap=1,  # Espaçamento entre os dias
                ygap=1,  # Espaçamento entre os turnos
            )
        )

        # Definir o título do gráfico
        fig.update_layout(
            title=f"Eficiência - Meta {meta}%",
            xaxis_title="Dia",
            yaxis_title="Linha",
            annotations=annotations,
            title_x=0.5,  # Centralizar o título
            xaxis_nticks=31,  # Definir o número de dias
            xaxis=dict(
                tickmode="linear",
                tickvals=list(range(1, 32)),  # Definir os dias
                ticktext=list(range(1, 32)),  # Definir os dias
            ),
            yaxis=dict(
                tickmode="linear",
                ticksuffix=" ",  # Adicionar um espaço no final
            ),
            plot_bgcolor="white",
            margin=dict({"t": 40, "b": 40, "l": 40, "r": 40}),
            font=dict({"family": "Inter"}),
        )

        fig.update_yaxes(
            autorange="reversed",
        )

        return fig

    def get_eff_bar_turn(self, dataframe: pd.DataFrame, meta: int = 90) -> go.Figure:
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
        # Definir a ordem desejada para 'turno'
        turno_order = ["NOT", "MAT", "VES"]

        # Converter 'turno' para uma variável categórica com a ordem desejada
        dataframe["turno"] = pd.Categorical(
            dataframe["turno"], categories=turno_order, ordered=True
        )

        # Agrupar, agregar e redefinir o índice
        df_grouped = (
            dataframe.groupby(["linha", "turno"], observed=True)
            .agg({"eficiencia": "mean", "total_produzido": "sum"})
            .reset_index()
        )

        # Ordenar o DataFrame por 'linha' e 'turno'
        df_grouped = df_grouped.sort_values(["linha", "turno"])

        # Ajustar produção total para caixas, dividindo por 10
        df_grouped["total_produzido"] = (df_grouped["total_produzido"] / 10).round(0)

        # Gráfico de barras
        fig = px.bar(
            df_grouped,
            orientation="h",
            x="eficiencia",
            y="linha",
            color="turno",
            barmode="group",
            hover_data={
                "total_produzido": True,
                "linha": False,
                "eficiencia": False,
            },
            color_discrete_map={
                "NOT": self.grey_500_color,
                "MAT": self.grey_600_color,
                "VES": self.grey_900_color,
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
            title_x=0.5,
            margin=dict({"t": 80, "b": 40, "l": 40, "r": 40}),
            legend=dict(
                {
                    "title_text": "Turno",
                    "traceorder": "normal",
                },
            ),
            template="plotly_white",
            font=dict({"family": "Inter"}),
        )

        # Ajustar valores de x para porcentagem
        fig.update_xaxes(tickformat=".0%")

        # Ajustar para aparecer todas as linhas
        fig.update_yaxes(
            autorange="reversed",
            tickvals=df_grouped["linha"].unique(),
        )

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
                name=f"Meta {meta}%",
                line=dict(dash="dash", color="blue"),
                hovertemplate="<b>Meta</b>: %{x:.1%}<br>",
            )
        )

        return fig

    def get_time_lost(
        self,
        df_info: pd.DataFrame,
        ind_type: IndicatorType,
        turn: str,
        working_minutes: pd.DataFrame = None,
    ) -> pd.DataFrame:
        """
        Este método é responsável por criar o dataframe de tempo perdido.

        Parâmetros:
        df_info (pd.DataFrame): DataFrame contendo os dados para o gráfico.
                                Deve incluir as colunas 'data_registro', 'turno' e 'eficiencia'.
        ind_type (IndicatorType): Tipo do indicador.

        Retorna:
        df_info_desc_times (pd.DataFrame): DataFrame com os dados de tempo perdido.
        """

        # Mapear pelo tipo do indicador
        ind_type_map = {
            IndicatorType.EFFICIENCY: self.times_data.desc_eff,
            IndicatorType.REPAIR: self.times_data.desc_rep,
            IndicatorType.PERFORMANCE: self.times_data.desc_perf,
        }

        # Conseguindo dataframe com tempos ajustados
        df_info_desc_times = self.times_data.get_times_discount(df_info, ind_type_map[ind_type])

        # Unir df_info_desc_times com working_minutes.
        if working_minutes is not None:
            df_info_desc_times = pd.concat(
                [df_info_desc_times, working_minutes], ignore_index=True, sort=False
            )

        # Filtrar por turno
        df_info_desc_times = (
            df_info_desc_times[df_info_desc_times["turno"] == turn]
            if turn != "TOT"
            else df_info_desc_times
        )

        # Se coluna "excedente" for nula, substituir pelo valor de "tempo_registro_min"
        df_info_desc_times.loc[df_info_desc_times["excedente"].isnull(), "excedente"] = (
            df_info_desc_times["tempo_registro_min"]
        )

        # Se motivo id for nulo e excedente for menor que 5 substituir motivo_nome por
        # "5min ou menos"
        df_info_desc_times.loc[
            (df_info_desc_times["motivo_id"].isnull()) & (df_info_desc_times["excedente"] <= 5),
            ["motivo_nome", "problema"],
        ] = ["5min ou menos", "Não apontado - 5min ou menos"]

        # Preencher onde motivo_nome for nulo
        df_info_desc_times["motivo_nome"].fillna("Motivo não apontado", inplace=True)

        df_info_desc_times.loc[
            (df_info_desc_times["motivo_id"] == 12)
            & (df_info_desc_times["problema"] == "Parada programada"),
            "problema",
        ] = "Parada Programada"

        # data_hora_final para datetime
        df_info_desc_times["data_hora_final"] = pd.to_datetime(
            df_info_desc_times["data_hora_final"]
        )

        return df_info_desc_times

    def adjust_df_for_bar_lost(self, df: pd.DataFrame, indicator: IndicatorType) -> pd.DataFrame:
        """
        Remove as paradas que não afetam o indicador.

        Parâmetros:
        - df: Dataframe contendo os dados
        - indicator: Define se é performance ou repair

        Retorno:
        - df: Dataframe contendo só as paradas que afetam.
        """

        indicator_actions = {
            IndicatorType.PERFORMANCE: lambda df: df[
                ~df["motivo_id"].isin(self.times_data.not_af_perf)
            ],
            IndicatorType.REPAIR: lambda df: df[df["motivo_id"].isin(self.times_data.af_rep)],
            IndicatorType.EFFICIENCY: lambda df: df[
                ~df["motivo_id"].isin(self.times_data.not_af_eff)
            ],
        }

        if indicator in indicator_actions:
            df = indicator_actions[indicator](df)

        return df

    def get_eff_bar_lost(self, df: pd.DataFrame, turn: str, checked: bool = False) -> go.Figure:
        """
        Retorna um gráfico de barras representando o tempo perdido que mais impacta a eficiência.

        Parâmetros:
        - df: DataFrame contendo os dados necessários para a criação do gráfico.
        - checked: Se True, retorna o gráfico de barras agrupado por motivo_nome e problema.

        Retorno:
        - fig: Objeto go.Figure contendo o gráfico de barras.
        """
        # Turno Map
        turn_map = {
            "NOT": "Noturno",
            "MAT": "Matutino",
            "VES": "Vespertino",
            "TOT": "Total",
        }

        # Remover linhas que não afetam a eficiência
        df = self.adjust_df_for_bar_lost(df, IndicatorType.EFFICIENCY)

        # ---------- df motivo ---------- #
        # Agrupar motivo_nome
        df_motivo = (
            df.groupby("motivo_nome")["excedente"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )

        # Preencher onde motivo_id for 3 e problema for nulo
        df.loc[
            (df["motivo_id"] == 3) & (df["problema"].isnull()),
            "problema",
        ] = "Refeição"

        # Preencher onde problema for nulo
        df.loc[:, "problema"] = df["problema"].fillna("Problema não informado")

        # ---------- df group ---------- #
        # Agrupar por motivo_nome e problema e calcular a soma do excedente
        df_grouped = df.groupby(["motivo_nome", "problema"]).agg({"excedente": "sum"}).reset_index()
        # Ordenar por excedente
        df_grouped = df_grouped.sort_values("excedente", ascending=False).head(8)

        # ---------- df problema ---------- #
        # Remover linhas onde motivo_nome é igual ao problema
        df = df[df["motivo_nome"] != df["problema"]]
        # Agrupar por problema
        df_problema = (
            df.groupby("problema")["excedente"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )

        # Motivo
        motive_bar = go.Bar(
            name="Motivo",
            x=df_motivo["motivo_nome"],
            y=df_motivo["excedente"],
            marker_color=self.grey_600_color,
        )

        motive_bar.update(
            hovertemplate="<b>Motivo</b>: %{x}<br><b>Tempo Perdido</b>: %{y:.0f} min<br>",
        )

        # Problema

        # Cria uma paleta de cores com os valores únicos na coluna 'problema'
        palette = sns.dark_palette("lightgray", df_grouped["problema"].nunique())

        # Converte as cores RGB para hexadecimal
        palette_hex = [mcolors.to_hex(color) for color in palette]

        # Cria um dicionário que mapeia cada valor único na coluna 'problema' para uma cor na paleta
        color_map = dict(zip(df_grouped["problema"].unique(), palette_hex))

        # Mapeia os valores na coluna 'problema' para as cores correspondentes
        df_grouped["color"] = df_grouped["problema"].map(color_map)

        problem_bar = go.Bar(
            name="Problema",
            x=df_problema["problema"],
            y=df_problema["excedente"],
            marker_color=self.grey_500_color,
            hovertemplate="<b>Problema</b>: %{x}<br><b>Tempo Perdido</b>: %{y:.0f} min<br>",
        )

        # Group
        group_bar = go.Bar(
            x=df_grouped["motivo_nome"],
            y=df_grouped["excedente"],
            customdata=df_grouped["problema"],
            hovertemplate="<b>Motivo</b>: %{customdata}<br><b>Tempo Perdido</b>: %{y:.0f} min<br>",
            marker_color=self.grey_500_color,
        )

        # Gráfico de barras
        fig = (
            go.Figure(data=[motive_bar, problem_bar])
            if not checked
            else go.Figure(data=[group_bar])
        )

        fig.update_layout(
            title=f"Tempo Perdido que mais impacta a Eficiência - {turn_map[turn]}",
            xaxis_title="Motivo/Problema",
            yaxis_title="Tempo Perdido",
            title_x=0.5,
            margin=dict({"t": 80, "b": 40, "l": 40, "r": 40}),
            template="plotly_white",
            font=dict({"family": "Inter"}),
            showlegend=False,
        )

        if not checked:
            fig.update_layout(showlegend=True)

        return fig

    def get_heat_turn(
        self,
        df_pivot: pd.DataFrame,
        indicator: IndicatorType,
        annotations: list,
        meta: int = 4,
    ) -> go.Figure:
        """
        Este método é responsável por criar o gráfico de reparos e performance, por turno.

        Parâmetros:
        dataframe (pd.DataFrame): DataFrame contendo os dados para o gráfico.
                                Deve incluir as colunas 'data_registro', 'turno' e o indicador.
        meta (int): Meta de eficiência a ser alcançada. Padrão: 4.
        annotations (bool): Se True, adiciona anotações com a média.

        Retorna:
        fig: Objeto plotly.graph_objects.Figure.

        O gráfico é um heatmap que mostra a média por maquina e data.
        A é colorida de verde se estiver abaixo de 4% e
        de vermelho se estiver acima de 4%.
        """

        indicator = indicator.value
        ind_capitalized = str(indicator).capitalize()

        # Criar escala de cores personalizada - cores do bootstrap
        colors = [
            [0, self.success_color],
            [0.04, self.success_color],
            [0.04, self.danger_color],
            [1, self.danger_color],
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
                zmax=1,
                hoverongaps=False,
                hovertemplate="Linha: %{y}<br>Dia: %{x}<br>Valor: %{z:.1%}",
                showscale=False,
                xgap=1,
                ygap=1,
            )
        )

        # Definir o título do gráfico
        fig.update_layout(
            title=f"{ind_capitalized} - Meta {meta}%",
            xaxis_title="Dia",
            yaxis_title="Linha",
            annotations=annotations,
            title_x=0.5,
            xaxis_nticks=31,
            xaxis=dict(
                tickmode="linear",
                tickvals=list(range(1, 32)),
                ticktext=list(range(1, 32)),
            ),
            yaxis=dict(
                tickmode="linear",
                ticksuffix=" ",  # Adicionar um espaço no final
            ),
            plot_bgcolor="white",
            margin=dict({"t": 40, "b": 40, "l": 40, "r": 40}),
            font=dict({"family": "Inter"}),
        )

        fig.update_yaxes(
            autorange="reversed",
        )

        return fig

    def get_bar_turn(
        self, dataframe: pd.DataFrame, indicator: IndicatorType, meta: int = 4
    ) -> go.Figure:
        """
        Este método é responsável por criar o gráfico, por turno.

        Parâmetros:
        dataframe (pd.DataFrame): DataFrame contendo os dados para o gráfico.
                                Deve incluir as colunas 'linha', 'turno',
                                'afeta o indicador.
        meta (int): Meta de eficiência a ser alcançada. Padrão: 4.

        Retorna:
        fig: Objeto plotly.graph_objects.Figure com o gráfico de eficiência.
        """

        indicator = indicator.value

        # Definir a ordem desejada para 'turno'
        turno_order = ["NOT", "MAT", "VES"]

        # Converter 'turno' para uma variável categórica com a ordem desejada
        dataframe["turno"] = pd.Categorical(
            dataframe["turno"], categories=turno_order, ordered=True
        )

        # Agrupar, agregar e redefinir o índice
        df_grouped = (
            dataframe.groupby(["linha", "turno"], observed=True)
            .agg({indicator: "mean", "afeta": "sum"})
            .reset_index()
        )

        # Ordenar o DataFrame por 'linha' e 'turno'
        df_grouped = df_grouped.sort_values(["linha", "turno"])

        # Gráfico de barras
        fig = px.bar(
            df_grouped,
            orientation="h",
            x=indicator,
            y="linha",
            color="turno",
            barmode="group",
            hover_data={
                "afeta": True,
                "linha": False,
                indicator: False,
            },
            color_discrete_map={
                "NOT": self.grey_500_color,
                "MAT": self.grey_600_color,
                "VES": self.grey_900_color,
            },
            labels={indicator: f"{indicator.capitalize()}"},
        )

        # Ajustar hover
        fig.update_traces(
            hovertemplate="<b>Linha</b>: %{y}<br>"
            "<b>Valor</b>: %{x:.1%}<br>"
            "<b>Tempo</b>: %{customdata[0]} min<br>",
        )

        # Definir o título do gráfico
        fig.update_layout(
            title=f"{indicator.capitalize()} por Linhas",
            xaxis_title=f"{indicator.capitalize()}",
            yaxis_title="Linha",
            title_x=0.5,
            margin=dict({"t": 80, "b": 40, "l": 40, "r": 40}),
            legend=dict(
                {
                    "title_text": "Turno",
                    "x": 0,
                    "y": 1,
                    "traceorder": "normal",
                    "font": {"family": "Inter", "size": 12},
                },
            ),
            template="plotly_white",
            font=dict({"family": "Inter"}),
        )

        # Ajustar valores de x para porcentagem e inverter o eixo x
        fig.update_xaxes(tickformat=".0%", autorange="reversed")

        # Ajustar para aparecer todas as linhas e or para a direita
        fig.update_yaxes(
            autorange="reversed",
            tickvals=df_grouped["linha"].unique(),
            side="right",
        )

        # Calcular a média geral
        avg_efficiency = df_grouped[indicator].mean()

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
                line=dict(dash="dash", color="blue"),
                hovertemplate="<b>Meta</b>: %{x:.1%}<br>",
            )
        )

        # Adicionar anotação
        fig.add_annotation(
            x=0.15,  # Posição x da anotação
            y=0.95,  # Posição y da anotação
            xref="paper",
            yref="paper",
            text=f"Meta: Abaixo de {meta}%",  # Texto da anotação
            showarrow=False,
            font=dict(size=12, color="black", family="Inter"),
            align="left",
            ax=20,
            ay=-30,
            bordercolor="#c7c7c7",
            borderwidth=2,
            borderpad=4,
            bgcolor="#ff7f0e",
            opacity=0.6,
        )

        return fig

    def get_bar_lost(
        self,
        df: pd.DataFrame,
        turn: str,
        indicator: IndicatorType,
        checked: bool = False,
    ) -> go.Figure:
        """
        Retorna um gráfico de barras representando o tempo perdido que mais impacta.

        Parâmetros:
        - df: DataFrame contendo os dados necessários para a criação do gráfico.
        - checked: Se True, retorna o gráfico de barras agrupado por motivo_nome e problema.

        Retorno:
        - fig: Objeto go.Figure contendo o gráfico de barras.
        """
        # Turno Map
        turn_map = {
            "NOT": "Noturno",
            "MAT": "Matutino",
            "VES": "Vespertino",
            "TOT": "Total",
        }

        df = self.adjust_df_for_bar_lost(df, indicator)

        # Preencher onde motivo_id for 12 e problema for nulo
        df.loc[
            (df["motivo_id"] == 12) & (df["problema"].isnull()),
            "problema",
        ] = "Parada Programada"

        # Preencher onde problema for nulo e motivo_id for 3
        df.loc[
            (df["motivo_id"] == 3) & (df["problema"].isnull()),
            "problema",
        ] = "Refeição"

        # Preencher onde problema for nulo
        df.loc[:, "problema"] = df["problema"].fillna("Problema não informado")

        # ---------- df motivo ---------- #
        # Agrupar motivo_nome
        df_motivo = (
            df.groupby("motivo_nome")["excedente"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )

        # ---------- df group ---------- #
        # Agrupar por motivo_nome e problema e calcular a soma do excedente
        df_grouped = df.groupby(["motivo_nome", "problema"]).agg({"excedente": "sum"}).reset_index()
        # Ordenar por excedente
        df_grouped = df_grouped.sort_values("excedente", ascending=False).head(8)

        # ---------- df problema ---------- #
        # Remover linhas onde motivo_nome é igual ao problema
        df = df[df["motivo_nome"] != df["problema"]]
        # Agrupar por problema
        df_problema = (
            df.groupby("problema")["excedente"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )

        # Motivo
        motive_bar = go.Bar(
            name="Motivo",
            x=df_motivo["motivo_nome"],
            y=df_motivo["excedente"],
            marker_color=self.grey_600_color,
        )

        motive_bar.update(
            hovertemplate="<b>Motivo</b>: %{x}<br><b>Tempo Perdido</b>: %{y:.0f} min<br>",
        )

        # Cria uma paleta de cores com os valores únicos na coluna 'problema'
        palette = sns.dark_palette("lightgray", df_grouped["problema"].nunique())

        # Converte as cores RGB para hexadecimal
        palette_hex = [mcolors.to_hex(color) for color in palette]

        # Cria um dicionário que mapeia cada valor único na coluna 'problema' para uma cor na paleta
        color_map = dict(zip(df_grouped["problema"].unique(), palette_hex))

        # Mapeia os valores na coluna 'problema' para as cores correspondentes
        df_grouped["color"] = df_grouped["problema"].map(color_map)

        # Problema
        problem_bar = go.Bar(
            name="Problema",
            x=df_problema["problema"],
            y=df_problema["excedente"],
            marker_color=self.grey_500_color,
            hovertemplate="<b>Problema</b>: %{x}<br><b>Tempo Perdido</b>: %{y:.0f} min<br>",
        )

        # Group
        group_bar = go.Bar(
            x=df_grouped["motivo_nome"],
            y=df_grouped["excedente"],
            customdata=df_grouped["problema"],
            hovertemplate="<b>Motivo</b>: %{customdata}<br><b>Tempo Perdido</b>: %{y:.0f} min<br>",
            marker_color=self.grey_500_color,
        )

        # Gráfico de barras
        fig = (
            go.Figure(data=[motive_bar, problem_bar])
            if not checked
            else go.Figure(data=[group_bar])
        )

        fig.update_layout(
            title=f"Maior impacto em {indicator.value.capitalize()} - {turn_map[turn]}",
            xaxis_title="Motivo/Problema",
            yaxis_title="Tempo Perdido",
            title_x=0.5,
            margin=dict({"t": 80, "b": 40, "l": 40, "r": 40}),
            template="plotly_white",
            font=dict({"family": "Inter"}),
            showlegend=False,
        )

        if not checked:
            fig.update_layout(showlegend=True)

        return fig

    def get_bar_stack_stops(self, df: pd.DataFrame, data) -> go.Figure:
        """
        Retorna um gráfico de barras empilhadas com o tempo perdido por maquina e seu motivo.
        """
        # Garantir que a data_registro tenha apenas a data
        df["data_registro"] = pd.to_datetime(df["data_registro"]).dt.date

        # Filtro pelo dia
        df = df[df["data_registro"] == pd.to_datetime(data).date()] if data is not None else df

        # Remover colunas que não serão necessárias
        df.drop(
            columns=[
                "feriado",
                "domingo",
                "sabado",
                "contagem_total_produzido",
                "contagem_total_ciclos",
                "usuario_id_occ",
                "solucao",
                "status",
            ],
            inplace=True,
        )

        # Substituir problema por "Não apontado - 5min ou menos" e motivo_nome por "5min ou menos"
        df.loc[df["tempo_registro_min"] <= 5, ["problema", "motivo_nome"]] = [
            "Não apontado - 5min ou menos",
            "5min ou menos",
        ]

        # Substituir valores nulos "Motivo não apontado" e em problema por "Não Informado"
        df.fillna({"motivo_nome": "Motivo não apontado", "problema": "Não Informado"}, inplace=True)

        # Ordenar os dados para que 'Rodando' sempre apareça por último
        df["sort"] = df["motivo_nome"] == "Rodando"
        df = df.sort_values(
            by=["linha", "data_registro", "sort", "tempo_registro_min"],
            ascending=[True, True, False, False],
        )
        df = df.drop(columns="sort")

        color_dict = {
            "5min ou menos": BSColorsEnum.GREY_500_COLOR.value,
            "Motivo não apontado": BSColorsEnum.GREY_600_COLOR.value,
            "Ajustes": BSColorsEnum.GRAY_COLOR.value,
            "Troca de Bobina": BSColorsEnum.GREY_400_COLOR.value,
            "Refeição": BSColorsEnum.ORANGE_COLOR.value,
            "Reunião": BSColorsEnum.SECONDARY_COLOR.value,
            "Café e Ginástica Laboral": BSColorsEnum.PRIMARY_COLOR.value,
            "Limpeza": BSColorsEnum.GREY_700_COLOR.value,
            "Manutenção Elétrica": BSColorsEnum.BLUE_DELFT_COLOR.value,
            "Manutenção Mecânica": BSColorsEnum.SPACE_CADET_COLOR.value,
            "Material em Falta": BSColorsEnum.GREY_900_COLOR.value,
            "Setup de Sabor": BSColorsEnum.PURPLE_COLOR.value,
            "Setup de Tamanho": BSColorsEnum.PINK_COLOR.value,
            "Parada Programada": BSColorsEnum.DANGER_COLOR.value,
            "Intervenção de Qualidade": BSColorsEnum.INDIGO_COLOR.value,
            "Linha Cheia": BSColorsEnum.TEAL_COLOR.value,
            "Treinamento": BSColorsEnum.INFO_COLOR.value,
            "Limpeza Industrial": BSColorsEnum.WARNING_COLOR.value,
            "Troca de Filme": BSColorsEnum.GREY_800_COLOR.value,
            "Rodando": BSColorsEnum.SUCCESS_COLOR.value,
        }

        # Criação do gráfico de barras
        fig = px.bar(
            df,
            x="linha",
            y="tempo_registro_min",
            color="motivo_nome",
            barmode="stack",
            labels={
                "tempo_registro_min": "Tempo (min)",
                "linha": "Linha",
                "motivo_nome": "Motivo",
            },
            title="Tempo de Parada por Problema",
            color_discrete_map=color_dict,
        )

        # Adicionar título e labels
        layout_1 = dict(
            title_x=0.5,
            xaxis_title="Linha",
            yaxis_title="Tempo (min)",
            plot_bgcolor="white",
            margin=dict(t=40, b=40, l=40, r=40),
            xaxis=dict(
                categoryorder="category ascending",
                tickvals=df["linha"].unique(),
            ),
        )

        layout_2 = dict(xaxis_title="", yaxis_title="")

        fig.update_layout(layout_1 if df is not None else layout_2)

        return fig

    def get_production_pivot(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Retorna um DataFrame pivotado com a produção total por linha e dia.

        Parâmetros:
        - df: DataFrame contendo os dados de produção.

        Retorno:
        - df_pivot: DataFrame pivotado com a produção total por linha e dia.
        """

        # Ordenar por linha, data_registro
        df = df.sort_values(by=["linha", "data_registro"])

        # Remover as linhas 0
        df = df[df["linha"] != 0]

        # Manter apenas o dia de data_registro
        df["data_registro"] = pd.to_datetime(df["data_registro"], errors="coerce")
        df["dia"] = df["data_registro"].dt.day

        # Criar pivot table, com as datas como colunas e as linhas como índice
        df_pivot = df.pivot_table(
            index="dia",
            columns="linha",
            values="total_produzido",
            aggfunc="sum",
        )

        # Adicionar uma linha com o total produzido por dia/linha
        df_pivot["Total"] = df_pivot.sum(axis=1)

        return df_pivot
