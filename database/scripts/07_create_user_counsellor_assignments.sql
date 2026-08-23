CREATE TABLE user_counsellor_assignments (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    user_id INT UNSIGNED NOT NULL,
    counsellor_profile_id INT UNSIGNED NOT NULL,
    assigned_by_admin_id INT UNSIGNED NOT NULL,
    support_requirement VARCHAR(255) NULL,

    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_user_counsellor_assignment
        UNIQUE (user_id),

    CONSTRAINT fk_assignment_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_assignment_counsellor
        FOREIGN KEY (counsellor_profile_id)
        REFERENCES counsellor_profiles(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_assignment_admin
        FOREIGN KEY (assigned_by_admin_id)
        REFERENCES users(id)
        ON DELETE RESTRICT
);
