DROP FUNCTION IF EXISTS get_topic_frequencies(text,integer,integer);

CREATE OR REPLACE FUNCTION get_topic_frequencies(
	source_alias TEXT,
	n_rollback_months INT = 6,
 	n_top INT = 10
)
RETURNS TABLE (
    topic TEXT,
    frequency BIGINT
) AS $$
DECLARE
	latest_control_id INT;
BEGIN

	-- 1: Setup
	DROP TABLE IF EXISTS term_base;
	DROP TABLE IF EXISTS term_frequencies;

	CREATE TEMPORARY TABLE term_base(
		term TEXT,
		frequency INT
	);
	
	CREATE TEMPORARY TABLE term_frequencies(
		term TEXT,
		total_frequency BIGINT
	);

	-- 2: Filter terms on provided source alias (DEBT: should probably add a 'latest' field to this table at some point)
	SELECT MAX(c.control_id) INTO latest_control_id FROM public.control c;
	
	INSERT INTO term_base (
		term,
		frequency
	)
	SELECT 
		t.term,
		t.frequency
	FROM public.term t
	JOIN public.source s ON s.source_id = t.source_id
	JOIN public.control c ON c.control_id = t.control_id
	WHERE s.alias = source_alias
	AND c.control_id BETWEEN (latest_control_id - n_rollback_months) AND latest_control_id; -- NB: assumes each batch has been run in order (safe assumption but a bit unstable if I were creating this in production!)

	-- 3: Sum over the total frequency of each term in the database
	INSERT INTO term_frequencies (
		term,
		total_frequency
	)
	SELECT  
		tb.term AS topic,
		SUM(tb.frequency) AS total_frequency
	FROM term_base tb 
	GROUP BY tb.term;
	
	-- 4: Filter the results on the top 'n_top' results
	RETURN QUERY
	SELECT
		term, 
		total_frequency
	FROM term_frequencies
	ORDER BY total_frequency DESC
	LIMIT n_top;

END;
$$ LANGUAGE plpgsql;
