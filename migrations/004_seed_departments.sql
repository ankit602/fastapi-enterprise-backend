INSERT INTO departments (name, description, is_deleted, created_at, updated_at)
VALUES
('Engineering', 'Engineering Department', false, NOW(), NOW()),
('Sales', 'Sales Department', false, NOW(), NOW()),
('Marketing', 'Marketing Department', false, NOW(), NOW()),
('Human Resources', 'HR Department', false, NOW(), NOW()),
('Finance', 'Finance Department', false, NOW(), NOW())
ON CONFLICT (name) DO NOTHING;
