from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class InventoryItemCreate(BaseModel):
    product: str = Field(min_length=1, max_length=100)
    stock: int = Field(ge=0)

    @field_validator("product")
    @classmethod
    def validate_product(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Product name cannot be blank")

        return value


class InventoryItemResponse(InventoryItemCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class InventoryPageResponse(BaseModel):
    items: list[InventoryItemResponse]
    total: int
    skip: int
    limit: int
    has_next: bool