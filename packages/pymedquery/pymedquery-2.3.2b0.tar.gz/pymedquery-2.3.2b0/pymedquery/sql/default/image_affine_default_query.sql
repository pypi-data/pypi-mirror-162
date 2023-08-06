/*
This is a defualt query for extracting SERIES UID, AFFINE UID and MASK UID. Masks are only fethed if
that certain subquery is returned and this query is only used if affines are requested. 
The query is meant to be used by beginner user,
users that dont have the need for advanced queries and users that don't
want to learn SQL.

The query is designed to fetch all images from a certain project which is why
the project_id variable is formatted into the query.

parameters
--------------
project_id : str
    This is user defined variable that will filter patientIDs on a projectID.
result : List[Dict[str, List[Any]
    this is the result that you get in python only. Not in the SQL editor.


The view columns:
patient_uid | series_uid | mask_id |

*/
WITH subq1 AS (
        SELECT patient_uid FROM junction_img_table
        WHERE project_id LIKE '{project_id}'
        LIMIT {limit}
    ), 

    subq2 AS (
        SELECT a.patient_uid, b.series_uid, b.affine_uid FROM subq1 a
        LEFT JOIN multimodal_image_table b 
        ON a.patient_uid=b.patient_uid
    ),
    
    subq3 AS (
        SELECT a.*, b.mask_uid FROM  subq2 a
        LEFT JOIN mask_table b
        ON a.series_uid=b.series_uid
        WHERE mask_uid IS NOT NULL
    )

    SELECT * FROM {sub} 
