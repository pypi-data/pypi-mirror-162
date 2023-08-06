# Hoist

## Easy client-server communication

### Quick Example

```py
import hoist

server = hoist.start("test") # set "test" as the authentication key

@server.receive("hello")
async def hello(socket: hoist.Message, payload: dict) -> None:
    print("server got hello")
    await message.reply("hi")
```

```py
import hoist

@hoist.connect_to("http://localhost:5000", "test") # log in to the server with key "test"
async def main(server: hoist.Connection):
    @server.receive("hi")
    async def hello(message: hoist.Message, payload: dict):
        print("client got hi")

    await server.message("hello")
```
