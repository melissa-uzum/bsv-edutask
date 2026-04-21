import pytest
import os
import json
import pymongo

from src.util.dao import DAO


@pytest.fixture
def sut():
    """Fixture that provides a DAO connected to a temporary test collection.

    Creates a temporary validator file and collection in MongoDB for testing,
    yields the DAO instance, then cleans up by dropping the collection and
    removing the temporary validator file.
    """
    # ensure connection to the Docker MongoDB (with auth)
    os.environ['MONGO_URL'] = 'mongodb://root:root@localhost:27017'

    # define a test validator with required fields, type constraints, and uniqueItems
    test_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["name"],
            "properties": {
                "name": {
                    "bsonType": "string",
                    "description": "the name must be determined",
                    "uniqueItems": True
                },
                "status": {
                    "bsonType": "bool"
                }
            }
        }
    }

    # write the temporary validator file so DAO.__init__ can find it
    validator_path = './src/static/validators/test_collection.json'
    with open(validator_path, 'w') as f:
        json.dump(test_validator, f)

    # create the DAO (this connects to MongoDB and creates the collection)
    dao = DAO('test_collection')

    yield dao

    # teardown: drop the test collection and remove the validator file
    dao.drop()
    os.remove(validator_path)
