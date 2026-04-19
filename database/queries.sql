-- "Now Showing" Page
SELECT * FROM Active_Movies 
ORDER BY release_date DESC;

-- "Coming Soon" Page
SELECT * FROM Coming_Soon_Movies 
ORDER BY release_date ASC;