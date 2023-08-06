from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr, Field

from .py_object_id_field import PyObjectId


class User(BaseModel):
    id: str = Field(alias='userId')
    username: str
    profileId: PyObjectId
    name: str
    given_name: str
    family_name: str
    email:  EmailStr
    locale: str
    resources: dict
    email_verified: bool

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        use_enum_values = True,
        schema_extra = {
            'example': {
                'id': 'bf7fe257-d107-4f0d-9408-8b338ac318e7',
                'username': 'superusername', 
                'profileId': '62c999287f39adde61ed8fbd',
                'name': 'Jose Doe',
                'given_name': 'Jose',
                'family_name': 'Doe',
                'email': 'jose.doe@gmail.com',
                'locale': 'es',
                'resources': {
                  'custom-resource-name-1': {
                    'roles': ['citizen'],
                  },
                  'custom-resource-name-2': {
                    'roles': ['citizen'],
                  },
                  'account': {
                    'roles': [
                      'manage-account',
                      'manage-account-links',
                      'view-profile',
                    ],
                  },
                },
                'email_verified': True,
            }
        }
    
    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        return self.dict(by_alias=True, exclude_none=True)
