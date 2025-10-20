-- database: :memory:
SELECT  strftime(Fecha,'%m/%d/%Y %I:%M %p') AS Fecha
       ,strftime(Fecha,'%Y%m')              AS Periodo
       ,Categoria                           AS Categoria
       ,Persona                             AS Persona
       ,Comercio                            AS Comercio
       ,Descripcion                         AS Descripcion
       ,SUM(Monto)                          AS Total
FROM df
WHERE Categoria NOT IN ('Super')
GROUP BY  ALL
ORDER BY  Fecha DESC;