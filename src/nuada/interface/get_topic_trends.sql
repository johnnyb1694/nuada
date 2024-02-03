DROP FUNCTION IF EXISTS get_topic_trends(text,integer,integer);

CREATE OR REPLACE FUNCTION get_topic_trends(
	source_alias TEXT,
	n_rollback_months INT = 6,
 	min_term_occurrences INT = 25
)
RETURNS TABLE (
    topic TEXT,
    avg_growth NUMERIC
) AS $$
DECLARE
	latest_control_id INT;
BEGIN

	-- 1: Setup
	DROP TABLE IF EXISTS term_base;
	DROP TABLE IF EXISTS term_absent;
	DROP TABLE IF EXISTS term_complete;
	DROP TABLE IF EXISTS term_frequency;
	DROP TABLE IF EXISTS term_frequencies;
	DROP TABLE IF EXISTS term_growth;

	CREATE TEMPORARY TABLE term_base(
		control_id INT,
		term TEXT,
		frequency INT
	);

	CREATE TEMPORARY TABLE term_absent (
		control_id INT,
		term TEXT,
		frequency INT
	);

	CREATE TEMPORARY TABLE term_complete (
		control_id INT,
		term TEXT,
		frequency INT
	);

	CREATE TEMPORARY TABLE term_frequency (
		term TEXT,
		frequency INT
	);

	CREATE TEMPORARY TABLE term_frequencies (
		year INT,
		month INT,
		term TEXT,
		frequency INT,
		prior_frequency INT
	);

	CREATE TEMPORARY TABLE term_growth (
		year INT,
		month INT,
		term TEXT,
		frequency INT,
		prior_frequency INT,
		growth NUMERIC(10, 4)
	);

	-- 2: Filter terms on provided source alias (DEBT: should probably add a 'latest' field to this table at some point)
	SELECT MAX(c.control_id) INTO latest_control_id FROM public.control c;
	
	INSERT INTO term_base (
		control_id,
		term,
		frequency
	)
	SELECT 
		t.control_id,
		t.term,
		t.frequency
	FROM public.term t
	JOIN public.source s ON s.source_id = t.source_id
	JOIN public.control c ON c.control_id = t.control_id
	WHERE s.alias = source_alias
	AND c.control_id BETWEEN (latest_control_id - n_rollback_months) AND latest_control_id; -- NB: assumes each batch has been run in order (safe assumption but a bit unstable if I were creating this in production!)

	-- 3: Insert missing term-control combinations for relevant instances (remember that 'control' is a proxy for period under consideration)
	INSERT INTO term_absent (
		control_id, 
		term, 
		frequency
	)
	SELECT DISTINCT 
		c_uniq.control_id, 
		t_uniq.term, 
		0
	FROM (SELECT DISTINCT term FROM term_base) t_uniq
	CROSS JOIN (SELECT DISTINCT control_id FROM public.control) c_uniq
	WHERE NOT EXISTS (
		SELECT 1
		FROM public.term t
		WHERE t.term = t_uniq.term AND t.control_id = c_uniq.control_id
	);

	-- 4: Unionise both tables to complete the terms
	INSERT INTO term_complete (
		control_id,
		term,
		frequency
	)
	SELECT 
		tb.control_id,
		tb.term,
		tb.frequency
	FROM term_base tb
	UNION
	SELECT
		ta.control_id,
		ta.term,
		ta.frequency
	FROM term_absent ta;

	-- 5: Count the total frequencies of each term
	INSERT INTO term_frequency (
		term,
		frequency
	)
	SELECT
		tp.term,
		SUM(tp.frequency) AS total_frequency
	FROM term_base tp
	GROUP BY tp.term
	HAVING SUM(tp.frequency) > min_term_occurrences;

	-- 6: Compute reporting trend statistics
	INSERT INTO term_frequencies (
		year,
		month,
		term,
		frequency,
		prior_frequency
	)
	SELECT
		c.year,
		c.month,
		tc.term,
		tc.frequency,
		LAG(tc.frequency, 1) OVER (PARTITION BY tc.term ORDER BY tc.control_id) AS prior_frequency
	FROM term_complete tc
	JOIN public.control c ON c.control_id = tc.control_id
	JOIN term_frequency tf ON tf.term = tc.term; -- NB: filtering join which eliminates terms that are relatively infrequent

	INSERT INTO term_growth (
		year,
		month,
		term,
		frequency,
		prior_frequency,
		growth
	)
	SELECT 
		tf.year,
		tf.month,
		tf.term,
		tf.frequency,
		tf.prior_frequency,
		CASE WHEN tf.prior_frequency = 0 OR tf.frequency = 0 THEN 0 ELSE (tf.frequency::numeric - tf.prior_frequency::numeric) END AS growth
	FROM term_frequencies tf;

    RETURN QUERY
	SELECT  
		tg.term AS topic,
		AVG(tg.growth) AS avg_growth
	FROM term_growth tg 
	GROUP BY tg.term;

END;
$$ LANGUAGE plpgsql;
