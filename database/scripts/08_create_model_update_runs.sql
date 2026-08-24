CREATE TABLE model_update_runs (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    version_label VARCHAR(100) NOT NULL,
    model_directory VARCHAR(255) NOT NULL,
    status ENUM(
        'registered',
        'evaluated',
        'deployed',
        'rejected'
    ) NOT NULL DEFAULT 'registered',
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    source_record_count INT UNSIGNED NOT NULL DEFAULT 0,
    notes VARCHAR(500) NULL,
    created_by_admin_id INT UNSIGNED NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    deployed_at TIMESTAMP NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_model_update_version_label (version_label),
    CONSTRAINT fk_model_update_admin
        FOREIGN KEY (created_by_admin_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);

INSERT INTO model_update_runs (
    version_label,
    model_directory,
    status,
    is_active,
    source_record_count,
    notes
)
VALUES (
    'Initial validated DistilBERT',
    'selected-distilbert-emotion',
    'deployed',
    TRUE,
    0,
    'Baseline deployed model selected during project model evaluation.'
);
