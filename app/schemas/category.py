from pydantic import BaseModel, ConfigDict, Field
class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CategoryRead(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
