from sqlalchemy import Integer, VARCHAR

REPORTING_SCHEMAS = {
    "question_groups": {
        "question_group_id": {
            "type": Integer,
            "primary_key": True,
            "nullable": False
        },
        "question_group_name": {
            "type": VARCHAR(255),
            "nullable": False
        },
        "description": {
            "type": VARCHAR(255)
        }
    },
    "question_items": {
        "question_item_id": {
            "type": VARCHAR(50),
            "primary_key": True,
            "nullable": False
        },
        "question_group_id": {
            "type": Integer,
            "nullable": False,
            "foreign_key": "reporting.question_groups.question_group_id"
        },
        "type_major": {
            "type": VARCHAR(255)
        },
        "type_minor": {
            "type": VARCHAR(255)
        }
    },
    "question_items_dict": {
        "question_item_id": {
            "type": VARCHAR(50),
            "nullable": False,
            "primary_key": True,
            "foreign_key": "reporting.question_items.question_item_id"
        },
        "lang": {
            "type": VARCHAR(2),
            "primary_key": True,
            "nullable": False
        },
        "label_major": {
            "type": VARCHAR(10000),
            "nullable": True
        },
        "label_major_short": {
            "type": VARCHAR(255),
            "nullable": True
        },
        "label_minor": {
            "type": VARCHAR(255),
            "nullable": True
        }
    },
    "subquestions": {
        "subquestion_id": {
            "type": VARCHAR(50),
            "primary_key": True,
            "nullable": False
        },
        "question_item_id": {
            "type": VARCHAR(50),
            "nullable": False,
            "foreign_key": "reporting.question_items.question_item_id"
        }
    },
    "respondents": {
        "respondent_id": {
            "type": Integer,
            "primary_key": True,
            "nullable": False
        }
    }
}