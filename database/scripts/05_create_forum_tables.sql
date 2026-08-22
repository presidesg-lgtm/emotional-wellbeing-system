USE emotional_wellbeing;


CREATE TABLE IF NOT EXISTS forum_posts (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    user_id INT UNSIGNED NOT NULL,

    content TEXT NOT NULL,

    is_hidden BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_forum_post_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS forum_reports (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    post_id INT UNSIGNED NOT NULL,

    reported_by_user_id INT UNSIGNED NOT NULL,

    reason VARCHAR(255) NOT NULL,

    status ENUM(
        'pending',
        'reviewed',
        'dismissed'
    ) NOT NULL DEFAULT 'pending',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    reviewed_at TIMESTAMP NULL DEFAULT NULL,

    CONSTRAINT uq_forum_report_user_post
        UNIQUE (
            post_id,
            reported_by_user_id
        ),

    CONSTRAINT fk_forum_report_post
        FOREIGN KEY (post_id)
        REFERENCES forum_posts(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_forum_report_user
        FOREIGN KEY (reported_by_user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);