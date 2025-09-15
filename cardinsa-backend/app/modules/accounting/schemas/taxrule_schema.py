from pydantic import BaseModel, ConfigDict
from typing import Optional

class TaxRuleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class TaxRuleCreate(TaxRuleBase):
    pass

class TaxRuleUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class TaxRuleRead(TaxRuleBase):
    id: str
