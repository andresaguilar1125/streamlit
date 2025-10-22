-- database :memory:
WITH BudgetTable AS
(
	SELECT * FROM
	( VALUES         
        ('Familiar', 65000),
        ('Medico', 50000),
        ('Recibos', 120000),
        ('Restaurantes', 120000),
        ('Super', 300000), 
        ('Viajes', 120000)
	) AS t(Categoria, Budget)
)
SELECT  b.Categoria
       ,b.Budget
       ,COALESCE(SUM(d.Monto),0)            AS Sum
       ,b.Budget - COALESCE(SUM(d.Monto),0) AS Remaining
FROM BudgetTable b
LEFT JOIN df d
ON b.Categoria = d.Categoria
GROUP BY  b.Categoria
         ,b.Budget
ORDER BY  b.Categoria;