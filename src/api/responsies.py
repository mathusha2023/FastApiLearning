from fastapi import Response


class PNGResponse(Response):
    media_type = "image/png"


def response404(description: str, message: str):
    return {404:
        {
            "description": description,
            "content": {
                "application/json": {
                    "example": {
                        "detail": message
                    }
                }
            }
        }
    }
