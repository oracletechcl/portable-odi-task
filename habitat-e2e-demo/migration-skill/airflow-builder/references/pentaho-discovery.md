# Pentaho discovery

Run the ODI builder inventory tool or equivalent deterministic XML inspection.
Read all selected KJB/KTR files. Capture job entries, enabled hops, evaluated
success/failure/unconditional transitions, variables, shell/mail/file/database
boundaries, fields/types/order, separators/encodings, names, dates, and retries.

Map each job entry to a DAG task or TaskGroup and each transformation to an
importable module. Map Pentaho failure hops to Airflow trigger rules or explicit
failure callbacks; never silently flatten an abort/notification branch.
