from pydantic import BaseModel, ConfigDict

class Context:
    repo: str 
    file: str
    uid: str
    lines: list[int[
