# Even History

## Why do we need this?

Well, you probably don't. But I needed it for something personal that I was working on and thought
it would be good to show it off so that maybe it can help someone else.

## Usecases

The library is quite simple, you only have to have two classes that satisfy
the `IEventHistoryService` and `IEventService` protocols.

The `IEventHistoryService` is a simple protocol, that has a `save` method which
takes in only two arguments, one the object its trying to save, called `event_object`

(NOTE its not a keyword argument in the `TransactionService` so the first position
argument would be expected to be event_object.) The `IEventService` protocol is very
similar to it and has two methods, `save` and `update` methods. Both of which have the
same calling signature, the first argument is `event_object` which is the object that
you want to save and the other arugment is a keyword argument called `session` .

The `session` is the `ContextManager` provided by many database library for
ACID transactions. PyMongo provides it too, using the `start_session` method of
`pymongo.MongoClient` class.

## What does it do

This library is very simple, in fact quite a dumb one to begin with but it does
its simple job well. The idea is to use the already existing services with your
business entity (models). The requirement for this library is quite simple too, all
you need is a service layer to save and update date in your desired database.
You would also need a context manager, either make one yourself (refer to the `tests`

directory to see how to make a simple one) or use the one provided with your database
drivers/library.

After which, all you need to do is to initialise the `TransactionService` class with
these services as arguments.

For example, 

```python
...

@dataclasses.dataclass
class Event:
    ...
    # these two are required fields to be included in
    # your model for TransactionService to work properly.
    timestampt: datetime.datetime
    version: int = 0

class EventService:
    ...

    def save(self, event_object, session=None):
        ...

    def update(self, event_object, session=None):
        ...

class EventHistoryService:
    ...

    def save(self, event_object, session=None):
        ...

client = pymongo.MongoClient("url-to-some-replica-set")

your_event_object = Event(**some_data_dict)

transaction_service = event_history.TransactionService(
    EventService(),
    EventHistoryService(),
)

with client.start_session() as session:
    transaction_service.save(your_event_object, session=session)

logging.info("All done! Now check your database.")

...

your_event_object = Event(**some_updated_dict)

with client.start_session() as session:
    transaction_service.update(your_event_object, session=session)

loggin.info("It should be updated! Now check your database.)

```

This is a minimal example that shows that basic use of this Transaction service with
PyMongo sessions but as explained earlier, this library is designed to be context
agnostic and can handler it with any context manager you provide (as long as your
`save` and `update` methods in service classes is able to use them).

---

Finally, you can use this library if you want - however, I don't think this is an
actual library since all its doing is abstracting away some of the burden of writing
further abstractions on top of your service layers. So, if you can just look at
the pattern and come up with your own simple abstraction, that would be better than
adding a dependency (this sideproject) in your projects.

For a fully fledged example, take a look at the `example` directory and the code inside.
It shows how it can be used with `pymongo` library and how it can work very nicely
with it.
