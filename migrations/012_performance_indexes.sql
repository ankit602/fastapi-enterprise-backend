CREATE INDEX IF NOT EXISTS ix_employees_department_deleted
ON employees (department_id, is_deleted);

CREATE INDEX IF NOT EXISTS ix_employees_deleted_id
ON employees (is_deleted, id);

CREATE INDEX IF NOT EXISTS ix_employees_email_deleted
ON employees (email, is_deleted);

CREATE INDEX IF NOT EXISTS ix_departments_deleted_id
ON departments (is_deleted, id);

CREATE INDEX IF NOT EXISTS ix_users_email_deleted
ON users (email, is_deleted);

CREATE INDEX IF NOT EXISTS ix_users_active_deleted
ON users (is_active, is_deleted);

CREATE INDEX IF NOT EXISTS ix_background_jobs_status_created
ON background_jobs (status, created_at);

CREATE INDEX IF NOT EXISTS ix_background_jobs_type_status
ON background_jobs (job_type, status);
