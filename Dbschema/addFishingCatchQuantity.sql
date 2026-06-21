ALTER TABLE tool_templates
    ADD COLUMN fishing_catch_quantity INT NOT NULL DEFAULT 1
        COMMENT 'number of fish caught per successful fishing attempt'
        AFTER fishing_success_rate,
    ADD CONSTRAINT chk_tool_templates_fishing_catch_quantity
        CHECK (fishing_catch_quantity > 0);

UPDATE tool_templates
INNER JOIN items
    ON items.id = tool_templates.item_id
SET tool_templates.fishing_catch_quantity = CASE items.code
    WHEN 'bamboo_rod' THEN 2
    WHEN 'iron_rod' THEN 3
    WHEN 'legendary_rod' THEN 5
    ELSE tool_templates.fishing_catch_quantity
END
WHERE items.code IN (
    'bamboo_rod',
    'iron_rod',
    'legendary_rod'
);
