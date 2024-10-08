USE TOTVSDB

SELECT 
    T1.CYV_CDMQ AS "Codigo_Maquina"
    , T2.CYB_DSMQ AS "Descricao_Maquina"
    , T1.CYV_QTATRP AS "Quantidade_Atropelamento"
    , T1.CYV_DTRPBG AS "Data_Registro"
    , T1.CYV_HRRPBG AS "Hora_Registro"
    , T1.CYV_CDUSRP AS "Usuario_Registro"
    , COALESCE(
        CASE WHEN CHARINDEX(T1.CYV_CDUSRP, T3.X6_CONTEUD) > 0 THEN 'Fabrica 1' END,
        CASE WHEN CHARINDEX(T1.CYV_CDUSRP, T4.X6_CONTEUD) > 0 THEN 'Fabrica 2' END,
        'Não identificado'
      ) AS "Fabrica"
FROM CYV000 (NOLOCK) AS T1
JOIN CYB000 (NOLOCK) AS T2 ON T1.CYV_FILIAL = T2.CYB_FILIAL AND T1.CYV_CDMQ = T2.CYB_CDMQ AND T2.D_E_L_E_T_ <> '*'
LEFT JOIN SX6000 (NOLOCK) AS T3 ON T3.X6_VAR = 'MV_X_USRF1'
LEFT JOIN SX6000 (NOLOCK) AS T4 ON T4.X6_VAR = 'MV_X_USRF2'
WHERE T1.D_E_L_E_T_ <> '*' AND T1.CYV_FILIAL = '0101' AND T1.CYV_CDMQ LIKE 'AMS%' AND T1.CYV_DTRPBG BETWEEN '20240501' AND '20240531'
ORDER BY T1.CYV_DTRPBG, T1.CYV_CDMQ, T1.CYV_HRRPBG