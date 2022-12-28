CLEANING = [
        {
            "name": "filter_out_non_consent",
            "filter_by": "string",
            "question": "q0",
            "condition": "keep",
            "value": "Ja"
            },
        {
            "name": "filter_out_age",
            "question": "qx",
            "filter_by": "int",
            "condition": "bigger_than",
            "value": 99
            }
        ]
