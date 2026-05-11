UPDATE sources
SET is_active = FALSE
WHERE parser_key = 'rammstein_live'
  AND is_active = TRUE;
