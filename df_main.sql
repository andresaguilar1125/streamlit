SELECT
    strftime('%m-%d-%y %I:%M %p', CAST(Fecha AS TIMESTAMP)) AS Fecha,
    strftime('%m-%d-%Y', CAST(Fecha AS TIMESTAMP)) AS Dia,
    strftime('%Y%m', CAST(Fecha AS TIMESTAMP)) AS Periodo,
    CASE WHEN CAST(strftime('%d', CAST(Fecha AS TIMESTAMP)) AS INTEGER) >= 15 THEN 'Q2' ELSE 'Q1' END AS Quincena,
    CASE 
        WHEN CAST(strftime('%d', CAST(Fecha AS TIMESTAMP)) AS INTEGER) BETWEEN 1 AND 7 THEN 'S1'
        WHEN CAST(strftime('%d', CAST(Fecha AS TIMESTAMP)) AS INTEGER) BETWEEN 8 AND 14 THEN 'S2'
        WHEN CAST(strftime('%d', CAST(Fecha AS TIMESTAMP)) AS INTEGER) BETWEEN 15 AND 21 THEN 'S3'
        ELSE 'S4'
    END AS Semana,
    Categoria,
    Persona,
    Comercio,
    Descripcion,
    Grupo,
    CAST(REPLACE(CAST(Monto AS VARCHAR), ',', '') AS INTEGER) AS Monto
FROM df
WHERE TRUE
  AND {filters}
ORDER BY Fecha DESC
