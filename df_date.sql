-- database: :memory:
SELECT  strftime(Fecha,'%m/%d/%y') AS Dia
       ,Categoria                  AS Categoria
       ,SUM(Monto)                 AS Total
FROM df
GROUP BY  Dia
         ,Categoria
ORDER BY  Dia DESC;