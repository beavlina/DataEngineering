/*
1.
Вивести кількість фільмів в кожній категорії.
Результат відсортувати за спаданням.
*/
SELECT 
	c.category_id,
	c."name",
	COUNT(f.film_id) AS film_count
FROM film_category f
INNER JOIN category c
ON f.category_id = c.category_id
GROUP BY 
	c.category_id,
	c."name" 
ORDER BY film_count DESC;

--OR

SELECT 
	category, 
	COUNT(fid) AS film_count
FROM public.film_list
GROUP BY category 
ORDER BY film_count DESC;

/*
2.
Вивести 10 акторів, чиї фільми брали на прокат найбільше.
Результат відсортувати за спаданням.
*/
SELECT
	CONCAT(a.first_name, ' ', a.last_name) AS fullname_actor,
	COUNT(r.rental_id) AS rental_count
FROM rental r 
INNER JOIN inventory i
ON r.inventory_id = i.inventory_id 
INNER JOIN film_actor fa 
ON i.film_id = fa.film_id 
INNER JOIN actor a 
ON fa.actor_id = a.actor_id 
GROUP BY CONCAT(a.first_name, ' ', a.last_name)
ORDER BY rental_count DESC
LIMIT 10;

/*
3.
Вивести категорія фільмів, на яку було витрачено найбільше грошей
в прокаті
*/
SELECT 
	c.category_id,
	c."name",
	SUM(f.rental_rate) AS total_revenue
FROM rental r
INNER JOIN inventory i 
ON r.inventory_id = i.inventory_id 
INNER JOIN film f 
ON i.film_id  = f.film_id 
INNER JOIN film_category fc
ON f.film_id = fc.film_id 
INNER JOIN category c 
ON fc.category_id = c.category_id 
GROUP BY 
	c.category_id,
	c."name" 
ORDER BY total_revenue DESC
LIMIT 1;

/*
4.
Вивести назви фільмів, яких не має в inventory.
Запит має бути без оператора IN
*/
SELECT 
	f.title	
FROM film f 
LEFT JOIN inventory i
ON f.film_id = i.film_id 
WHERE i.film_id IS NULL;

--OR

SELECT
	f.title  
FROM film f
WHERE 
	NOT EXISTS (
	SELECT 
		1
	FROM inventory i 
	WHERE 
	f.film_id = i.film_id);
/*
5.
Вивести топ 3 актори, які найбільше зʼявлялись в категорії фільмів “Children”.
*/
SELECT 
	CONCAT(a.first_name, ' ', a.last_name) AS fullname_actor,
	COUNT(*) AS actor_counter
FROM film_actor fa 
INNER JOIN film f 
ON fa.film_id = f.film_id 
INNER JOIN actor a 
ON fa.actor_id = a.actor_id 
INNER JOIN film_category fc 
ON fc.film_id = f.film_id 
INNER JOIN category c
ON fc.category_id = c.category_id 
WHERE 
	c."name" = 'Children'
GROUP BY CONCAT(a.first_name, ' ', a.last_name)
ORDER BY actor_counter DESC
LIMIT 3;