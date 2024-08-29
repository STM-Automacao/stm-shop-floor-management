USE TOTVSDB

SELECT SD3.D3_FILIAL as Filial,
      SD3.D3_COD as CodigoProduto,
      SB1.B1_DESC as DescricaoProduto,
      SD3.D3_UM as UnidadeMedida,
      SD3.D3_QUANT as Quantidade,
      SD3.D3_CF as CodigoFornecedor,
      SD3.D3_EMISSAO as DataEmissao,
      SD3.D3_GRUPO as Grupo,
      SD3.D3_CUSTO1 as CustoUnitario,
      SD3.D3_USUARIO as Usuario
FROM SD3000 as SD3
INNER JOIN SB1000 as SB1 ON SB1.B1_COD = SD3.D3_COD AND (LEFT(SD3.D3_FILIAL, 2) = SB1.B1_FILIAL) AND SB1.D_E_L_E_T_ <> '*'
WHERE SD3.D_E_L_E_T_ <> '*' AND SD3.D3_EMISSAO > '20240801' AND SD3.D3_DOC = 'INVENT'

-- DE0: Pode representar um tipo de movimento de entrada, como uma devolução de mercadoria.
-- RE0: Pode representar um tipo de movimento de saída, como uma venda/remessa de mercadoria.
