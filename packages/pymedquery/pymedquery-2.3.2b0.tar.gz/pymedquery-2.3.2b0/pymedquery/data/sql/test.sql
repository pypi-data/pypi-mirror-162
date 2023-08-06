WITH subq1 AS (
    SELECT * FROM patient_table
    WHERE age in ('40-49', '50-59')
    LIMIT 20
    ), 

    subq2 AS (
        SELECT a.patient_uid, b.series_uid FROM subq1 a
        LEFT JOIN {name_table} b 
        ON a.patient_uid=b.patient_uid
    ),
    
    subq3 AS (
        SELECT a.*, b.mask_uid FROM  subq2 a
        LEFT JOIN mask_table b
        ON a.series_uid=b.series_uid
    )

    SELECT * FROM subq3 WHERE mask_uid IS NOT NULL
