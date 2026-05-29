UPDATE employees
SET
    salary = COALESCE(salary, FLOOR(RANDOM() * 90000 + 30000)::int),
    department_id = COALESCE(department_id, FLOOR(RANDOM() * 5 + 1)::int),
    is_deleted = COALESCE(is_deleted, false),
    created_at = COALESCE(created_at, NOW()),
    updated_at = COALESCE(updated_at, NOW())
WHERE salary IS NULL
   OR department_id IS NULL
   OR is_deleted IS NULL
   OR created_at IS NULL
   OR updated_at IS NULL;
