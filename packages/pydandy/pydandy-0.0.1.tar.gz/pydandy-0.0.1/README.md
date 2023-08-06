# Pydandy

Pydandtic + Handy

A lightweight "Database", built on top of [Pydandtic](https://pydantic-docs.helpmanual.io/). It is currently under development, but the intent is to support in-memory, file, and directory storage options and eventually an Async variant. For the file and directory modes, the data will be backed by either one or manyu JSON files. The main database is also meant to provide a slim ORM-like interface for querying the data.

## Examples
```python
from pydantic import BaseModel
from pydandy import PydandyDB

# Create an in-memory database
db = PydandyDB()
# Add User Model to the database

@db.register()
class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    # You can use any model, as long you provide a __hash__
    def __hash__(self):
        return self.id

# Add a new Record to Users
db.User.add(
    User(
        id=1,
        first_name="John",
        last_name="Baz",
    )
)

# Get your record back
user = db.User.get(1)

# Filter for records
db.User.filter(lambda record: record.first_name.startswith("J"))
```

## Motivation
Mostly just because, but also because I occasionaly finding myself wanting a small data, portable data store. This seemed like fun project idea, and I really Pydandtic, so it worked out.

## Contributing
At this stage, I am not accepting contributions. Mostly because I am still trying to shape out the core functionality. However, this should change soon™ if you are interested in helping out.