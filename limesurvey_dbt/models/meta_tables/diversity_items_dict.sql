SELECT
    diversity_items.diversity_item_id
    , mapping_diversity_items.lang
    , mapping_diversity_items.label_long
FROM {{ ref('diversity_items') }} AS diversity_items
JOIN {{ ref('mapping_diversity_items') }} AS mapping_diversity_items
ON diversity_items.diversity_item_id = mapping_diversity_items.diversity_item_id
