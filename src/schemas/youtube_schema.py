YOUTUBE_SCHEMA = {
    "type": "object",
    "properties": {
        "intro": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string"
                }
            },
            "required": [
                "text"
            ],
            "additionalProperties": False
        },
        "youtube": {
            "type": "object",
            "properties": {
                "subtitle": {
                    "type": "string"
                }
            },
            "required": [
                "subtitle"
            ],
            "additionalProperties": False
        },
        "thumbnail": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string"
                },
                "prompt": {
                    "type": "string"
                }
            },
            "required": [
                "title",
                "prompt"
            ],
            "additionalProperties": False
        }
    },
    "required": [
        "intro",
        "youtube",
        "thumbnail"
    ],
    "additionalProperties": False
}