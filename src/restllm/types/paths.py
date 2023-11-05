from fastapi import Path

id_path = Path(
    ...,
    gt=0,
    description="Whole positiv number corresponding to the ID of the ressource.",
    examples=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    openapi_examples={str(i): {"value": i} for i in range(1, 11)},
)
index_path = Path(
    ...,
    ge=0,
    description="Whole positiv number or 0, corresponding to the Index of the chat message.",
    examples=[0, 1, 2],
    openapi_examples={str(i): {"value": i} for i in range(4)},
)
payload_path = Path(..., description="Encrypted payload created from share endpoint.")
signature_path = Path(..., description="Payload signature created from share endpoint.")
