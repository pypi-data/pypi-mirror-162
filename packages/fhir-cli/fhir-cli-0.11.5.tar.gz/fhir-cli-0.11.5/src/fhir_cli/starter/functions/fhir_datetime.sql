CREATE FUNCTION fhir_datetime(datetime timestamp) RETURNS text AS $$
BEGIN
    RETURN to_char(datetime, 'YYYY-MM-DD"T"HH:MI:SS+02:00');
END;
$$ LANGUAGE plpgsql;
