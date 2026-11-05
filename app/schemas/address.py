from pydantic import BaseModel, ConfigDict, Field


class AddressCreate(BaseModel):
    city: str = Field(min_length=1, max_length=100)
    district: str = Field(min_length=1, max_length=100)
    street: str = Field(min_length=1, max_length=200)
    house: str = Field(min_length=1, max_length=30)


class AddressRead(AddressCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
