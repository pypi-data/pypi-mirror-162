/* This is a create table test sql*/

CREATE TABLE IF NOT EXISTS test_table (
    series_uid TEXT NOT NULL,
    pixel_spacing FLOAT[],
    series_number INTEGER,
    protocol_names TEXT,
    PRIMARY KEY (series_uid)
)
