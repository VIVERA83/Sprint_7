db = {
    "count_documents_in_person": {"quest": ["100", 30]},
    "get_document": {
        "quest": {
            "caf06d3f-19dc-4b7d-8aff-c0cbe7b643d0": {
                "id": "caf06d3f-19dc-4b7d-8aff-c0cbe7b643d0",
                "full_name": "Tracy Oliver",
                "role": "writer",
                "film_ids": ["{523f1a55-51fe-4d3c-a58d-30d8a61bb267}"],
            },
            "578593ee-3268-4cd4-b910-8a44cfd05b73": {
                "id": "578593ee-3268-4cd4-b910-8a44cfd05b73",
                "full_name": "Rafael Ferrer",
                "role": "actor",
                "film_ids": ["{2a090dde-f688-46fe-a9f4-b781a985275e}"],
            },
        },
    },
    "get_document_not_found": {
        "quest": {
            "2a090dde-f688-46fe-a9f4-b781a985275e": {"detail": "person not found"}
        }
    },
    "no_valid_id": {
        "quest": {
            "invalid id": {
                "detail": [
                    {
                        "loc": ["query", "person_id"],
                        "msg": "value is not a valid uuid",
                        "type": "type_error.uuid",
                    }
                ]
            }
        }
    },
    "search_by_name": {
        "quest": {
            "rafael Ferrer": [
                {
                    "id": "578593ee-3268-4cd4-b910-8a44cfd05b73",
                    "full_name": "Rafael Ferrer",
                    "role": "actor",
                    "film_ids": ["{2a090dde-f688-46fe-a9f4-b781a985275e}"],
                }
            ]
        }
    },
}
