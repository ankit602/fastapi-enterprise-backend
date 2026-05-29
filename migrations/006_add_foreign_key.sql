DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_employees_department'
          AND table_name = 'employees'
    ) THEN
        ALTER TABLE employees
        ADD CONSTRAINT fk_employees_department
        FOREIGN KEY (department_id)
        REFERENCES departments(id);
    END IF;
END$$;
