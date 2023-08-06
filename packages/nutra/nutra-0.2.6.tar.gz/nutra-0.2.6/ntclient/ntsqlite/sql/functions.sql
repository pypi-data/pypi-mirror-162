--------------------------------
-- Recipes overview
--------------------------------
SELECT
  id,
  tagname,
  name,
  COUNT(recipe_id) AS n_foods,
  SUM(grams) AS grams,
  recipe.created AS created
FROM
  recipe
  LEFT JOIN recipe_dat ON recipe_id = id
GROUP BY
  id;

--------------------------------
-- Last sync
--------------------------------
-- SELECT
--   max((
--     SELECT
--       last_sync FROM profiles), (
--     SELECT
--       last_sync FROM biometric_log), (
--     SELECT
--       last_sync FROM recipes), (
--     SELECT
--       last_sync FROM food_log), (
--     SELECT
--       last_sync FROM recipe_log), (
--     SELECT
--       last_sync FROM rda)) AS last_sync;
