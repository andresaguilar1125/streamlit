-- database: :memory:

SELECT
    -- ========================================= 
    -- FECHAS
    -- =========================================
    strftime(Fecha, '%m-%d-%y %I:%M %p') AS Fecha,
    strftime(Fecha, '%m-%d-%Y') AS Dia,
    strftime(Fecha, '%Y%m') AS Periodo,
    CASE( WHEN EXTRACT(DAY FROM Fecha) >= 15 THEN 'Q2' ELSE 'Q1' END AS) Quincena, 
    ('W' || strftime(Fecha, '%W')) AS Semana,

    -- ========================================= 
    -- CSV
    -- =========================================
    Categoria,
    Persona,
    Comercio,
    Descripcion,
    Grupo,
    CAST(REPLACE(Monto, ',', '') AS INT) AS Monto

FROM df;
