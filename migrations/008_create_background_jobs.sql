CREATE TABLE IF NOT EXISTS background_jobs (
    id SERIAL PRIMARY KEY,
    job_type VARCHAR NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'PENDING',
    file_path VARCHAR NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_background_jobs_job_type ON background_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_background_jobs_status ON background_jobs(status);
