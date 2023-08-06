from pydantic import BaseModel


def to_sns(entity: BaseModel) -> dict:
    # send to sns
    SNSClient().send(entity)
    return {"status": 200}
