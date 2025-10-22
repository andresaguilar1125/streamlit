-- keep px.area as it stacks the values by default
SELECT
 strftime(Fecha,'%Y%m') AS Periodo
       ,SUM(Monto)               AS Total
       ,'Casa'                   AS Persona
       ,Grupo                    AS Grupo
FROM df
WHERE Categoria = 'Super'
AND Fecha BETWEEN '2025-06-01' AND '2025-12-31'
GROUP BY  ALL