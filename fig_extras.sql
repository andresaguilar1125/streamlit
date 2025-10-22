-- keep px.area as it stacks the values by default
SELECT
 strftime(Fecha,'%Y%m') AS Periodo
       ,SUM(Monto) as Total
       ,Categoria                   AS Categoria
      --  ,Persona                    AS Persona
FROM df
WHERE Categoria IN ('Familiar', 'Medico','Restaurantes')
AND Fecha BETWEEN '2025-06-01' AND '2025-12-31'
GROUP BY  Periodo, Categoria