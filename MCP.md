# Model Context Protocol

The Model Context Protocol is an open source protocol that standardizes how applications provide context to LLMs.
The motivation behind MCP is that models are only as good as the context we provide. This seems obvious now, but a year ago, when most AI applications were chatbots, you’d bring in context by copy-pasting or typing from other systems. Over the past year, we’ve seen these evolve into systems where the model has hooks into data and context, making it more powerful and personalized.


![alt text](/diagrams/mcp-1.png)

MCP lets us build servers that expose data and functionality to LLM applications. Its often described as the “a USB-C port for AI applicaitons”, providing a uniform way to connect LLMs to resources they can use.

Just as USB-C port provides a standardized way to connect your devices to various peripherals and accessories, MCP provides a standardized way to connect to AI models to different data sources and tools.

It may be easier to think of it as an API, but specifically designed for LLM interactions.  MCP servers can:

  - expose data through `Resources` (think of these sort of like GET endpoints; they are used to load information into the LLM’s context)
  - provide functionality through `Tools` (sort of like POST end points; they are used to execute code)
  - We can define interaction patterns through `Prompts` (resuable templates for LLM interactions)

---



Since models are only as good as the context provided to them. You can have an incredibly intelligent model at the frontier, but if it doesn't have the ability to connect to the outside world and pull in necessary data and context, it's not as useful as it can possibly be.

MCP helps build agents and complex workflows on top of LLMs. LLMs frequently need to intergrate with data and tools, and MCP provides:
- Pre-buillt intergrations that our LLM/AI application can plug into
- Flexibility swtich between differnt LLM providers and AI applications
- Best practices for securing your data within your infrastructure





### General Architecture

- **MCP hosts** are IDEs or AI tools (RooCode, GitHub Co-pilot, Claude Desktop)
  - [https://modelcontextprotocol.io/clients](https://modelcontextprotocol.io/clients)
- **MCP clients (protocol clients)** that maintain 1:1 connection with servers
- **MCP servers**: Light weight programs that each expose specific capabilities through MCP
- **Local data sources** like your computers’s files, databases, and servinces that MCP servers can securely access
- **Remote services** are exteral systems availble over the internet (e.g., through APIs) that MCP servers can connect

![alt text](/diagrams/mcp-2.png)

Everything that can be done with MCP can technically be done without it. MCP doesn't reinvent the wheel for things like tool use. It just aims to standardize how AI applications interact with external systems. This is why other AI competitors to Anthropic like OpenAI and Google have adopted MCP. An analogy I would use is it's like how web applications communicate with backends and other systems using REST, where you have a specified protocol, statelessness, and so on. MCP standardizes how AI applications interact with external systems. Instead of building the same integration for different data sources over and over again depending on the model or the data source, you build once and use everywhere.

### Core Primitives
![alt text](/diagrams/mcp-5.png)

**Tools** are functions that LLMs can call. They are the core building blocks that allow our LLM to interact with external systems, execute code, and access data that isn’t training data.



**Resources** are read-only data that an MCP server can expose to the LLM application. Resources are similar to GET endpoint request in a Rest API. They provide data but shouldn’t perform significant computation or have side effects. For examples, the resource can be a list of folders within a directory or the content of a file within a folder.

**Prompts** are reusable templates for LLM interactions.




### Key Takeaways

MCP shifts the burden and separates concerns cleanly. Build an MCP app and connect it to servers for whatever data you need. Want data from AWS? There's a server. Need Git access? There's a server. The goal is simple: use natural language to talk to data stores without writing all that logic.
![alt text](/diagrams/mcp-3.png)
The beauty is that these servers are reusable. An MCP server for Google Drive works with any MCP app you build. AI assistant, agent, desktop app. If it speaks MCP, it can use that server. Let your imagination run with all the data access you can bring to your application with minimal code.

![alt text](/diagrams/mcp-4.png)

The right way to frame this is that MCP creates different kinds of value for different people. There are four main buckets:

-For application developers, once your client is MCP-compatible, you can connect it to any server with zero extra work. 
- If you’re a tool or API provider—or anyone who wants to give LLMs access to relevant data—you build your MCP server once and instantly get adoption across a range of AI applications.
- For end users, this unlocks richer, more powerful AI systems. You’ve probably seen demos—whether it’s Cursor, WindSurf, or even our own first-party apps—where these systems have deep context, know things about you, and can act on your behalf in the real world.
- For end users, this unlocks richer, more powerful AI systems. You’ve probably seen demos—whether it’s Co-pilot, RooCode etc. these systems have deep context, know things about you, and can act on your behalf in the real world.
- For enterprises, MCP introduces a clean way to separate concerns. Say one team owns the data layer and another team is building AI products. In the pre-MCP world, every team would implement its own access method, including prompt logic and chunking to get the data they need and process into their AI application. With MCP, that data team builds and maintains a single MCP server. They publish the interface, document it, and every other team can plug into it. Teams move faster, and the organization operates more like a modern microservices architecture—each team owns their piece, and the whole roadmap accelerates.





**Who authors the MCP server?**
- You can build them yourself or use community ones. You can make a MCP server to wrap up access to some servince. Often the service provider itself will make their own MCP server implementation. We'll build our own.

**How is using MCP Server different from just calling a service’s API direclty?**
- You might be thinking MCP servers are just like APIs. You're not wrong. An analogy I would use is: MCP server as a gateway on top of an API. MCP servers provde tool schemas + functons. If you want to direclty call an API, you’ll be authoring those on your own (clarify using an example)

**What's the difference between MCP servers and tool/function calling?**
- MCP servers support tool use, but that's just one part. MCP servers provide tool plus schema + functions already defined for you. We will explore this in detail in the rest of this post.





## How can you create an MCP server?

Lets take the example of a server that exposes tools. This server needs to handle two main requests from clients clients:
- listing all the tools
- executing a particular tool with these arguments

There are two ways of creating an MCP server:
- Low level implementation: in this approach, we can direclty define and handle the various types of request (`ListToolsRequest`  and `CallToolRequest`). This approach allows you to customize every aspect of your sever
- High-level implementation using `FastMCP` : `FastMCP` is a high-level interface that makes building MCP servers faster and simpler. In this approach, you just focus on defining the tools are functions, and `FastMCP` handles all the protocol details

To create an MCP server using FastMCP, we initialize a `FastMCP` server labled `mcp` and decorating the functions with `@mcp.tools()` . `FastMCP` automatically generates the necessary schema based on type hints and docstrings



### Introductory Example

A FastMCP server is a collection of tools, resources and other MCP compoents. To create a server we start by instantiaing the `FastMCP` class.

Create a new file called `my_se rver.py` and add the following code:

``` python
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")
```

To add a tool that returns a simple greeting, write a function and decorate it with `@mcp.tool` to register it with the server:

``` python
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

In order to run the server with Python, we need to add a run statement to the `__main__` block of the server file.

``` python
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```
This lets us run the server with `python my_server.py`, using the default stdio transport, which is the standard way to expose an MCP server to a client.

Now that the server can be executed with python my_server.py, we can interact with it like any other MCP server.

In a new file, create a client and point it at the server file:

``` python
import asyncio
from fastmcp import Client

client = Client("my_server.py")

async def call_tool(name: str):
    async with client:
        result = await client.call_tool("greet", {"name": name})
        print(result)

asyncio.run(call_tool("Hanan"))

```

``` bash
➜  quickstart python my_client.py 
[06/24/25 09:12:08] INFO     Starting MCP server 'My MCP server.py:1246
                             Server' with transport                    
                             'stdio'                                   
[TextContent(type='text', text='Hello, Hanan!', annotations=None)]
```
A few key points:
- clients are asynchronous, so we need to use `asyncio.run`  to run the client
- we must enter a client context ( `async with client:` ) before using the client. We can make multiple client calls within the same context. 

> **Context Manager**
A context manager in Python is a pattern that ensures proper setup and clean up of resources. The `async with` statement is the asynchronous version of this pattern. 

**Do We Need **`async with client:`**?**
The FastMCP client needs to **establish a connection** to the server before it can make any requests. The `async with` statement handles this connection lifecycle automatically:
``` python
client = Client(mcp)

# When you enter the context:
async with client:
    # 1. Connection is established here
    # 2. MCP protocol handshake occurs
    # 3. Client is now ready to make requests
    
    result = await client.call_tool("greet", {"name": "Ford"})
    # You can make multiple calls here
    
# 4. Connection is automatically closed when exiting the context
```


### Key Takeaways:
- We have successfully equipped our LLM with a new capability (a greeting tool.)
This demonstrates the fundamental power of MCP: **turning any function into a tool that an LLM can use.**

- The Three-Step Pattern:
    1. Define a function with clear inputs and outputs
    2. Decorate it with `@mcp.tool` to register it with the server
    3. Run the server to make it available to LLM clients

- Deterministic Function Execution: Our greeting function is a  deterministic tool - given the same input (name), it always produces the same output. This is crucial for LLM reliability.

This simple example demonstrates that MCP isn't just about connecting to external APIs. It's about making any code accessible to LLMs in a standardized way. Your greeting function could be replaced with any business logic, and the LLM would use it the same way.



---

### Tools

Tools are the core building blocks that allow our LLM to interact with external systems, execute code, and access data that isn’t training data. Tools in FastMCP transform regular Python functions into capabilities that LLMs can invoke during conversations. When an LLM decides to use a tool:
1. It sends a request with parameters based on the tool’s schema.
2. FastMCP validates these parameters against your function’s signature.
3. Our function executes with the validated inputs.
4. The result is returned to the LLM, which can use it in its response.

![alt text](/diagrams/FunctionCalling.png)

This allows LLMs to perform tasks like querying databases, calling APIs, making calculations, or accessing files—extending their capabilities beyond what’s in their training data.

Creating a tool is as simple as decorating a Python function with `@mcp.tool`:

``` python
from fastmcp import FastMCP

mcp = FastMCP(name="CalculatorServer")

@mcp.tool
def add(a: int, b: int) -> int:
    """Adds two integer numbers together."""
    return a + b

```
When this tool is registered, FastMCP automatically:
- Uses the function name (`add`) as the tool name.
- Uses the function’s docstring (`Adds two integer numbers...`) as the tool description.
- Generates an input schema based on the function’s parameters and type annotations.
- Handles parameter validation and error reporting.


The way you define your Python function dictates how the tool appears and behaves for the LLM client.

>Functions with `*args` or `**kwargs` are not supported as tools. This restriction exists because FastMCP needs to generate a complete parameter schema for the MCP protocol, which isn’t possible with variable argument lists.



### Resources

Resources are read-only data that an MCP server can expose to the LLM application. Resources are similar to GET endpoint request in a Rest API. 
When a client requests a resource URI:
1. FastMCP finds the corresponding resource definition.
2. If it’s dynamic (defined by a function), the function is executed.
3. The content (text, JSON, binary data) is returned to the client.
This allows LLMs to access files, database content, configuration, or dynamically generated information relevant to the conversation.

``` python
from fastmcp import FastMCP

mcp = FastMCP(name="DataServer")

# Template URI includes {city} placeholder
@mcp.resource("weather://{city}/current")
def get_weather(city: str) -> dict:
    """Provides weather information for a specific city."""
    # In a real implementation, this would call a weather API
    # Here we're using simplified logic for example purposes
    return {
        "city": city.capitalize(),
        "temperature": 22,
        "condition": "Sunny",
        "unit": "celsius"
    }

# Template with multiple parameters
@mcp.resource("repos://{owner}/{repo}/info")
def get_repo_info(owner: str, repo: str) -> dict:
    """Retrieves information about a GitHub repository."""
    # In a real implementation, this would call the GitHub API
    return {
        "owner": owner,
        "name": repo,
        "full_name": f"{owner}/{repo}",
        "stars": 120,
        "forks": 48
    }
```

They provide data but shouldn’t perfrom significant computation or have side effects. For examples, the resource can be a list of folders within a directory or the content of a file within a folder. 








### Prompt Template

Server can also provide a prompt template. Prompts are reusable message templates that help LLMs generate structured, purposeful responses. FastMCP simplifies defining these templates, primarily using the `@mcp.prompt` decorator.

Prompts provide parameterized message templates for LLMs. When a client requests a prompt:

1. FastMCP finds the corresponding prompt definition.
2. If it has parameters, they are validated against the function signature.
3. The function executes with the validated inputs.
4. The generated message(s) are returned to the LLM to guide its response.

This allows us to define consistent, reusable templates that LLMs can use across different clients and contexts.

The most common way to define a prompt is by decorating a Python function. The decorator uses the function name as the prompt’s identifier.

``` python
from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptMessage, TextContent

mcp = FastMCP(name="PromptServer")

# Basic prompt returning a string (converted to user message automatically)
@mcp.prompt
def ask_about_topic(topic: str) -> str:
    """Generates a user message asking for an explanation of a topic."""
    return f"Can you please explain the concept of '{topic}'?"

# Prompt returning a specific message type
@mcp.prompt
def generate_code_request(language: str, task_description: str) -> PromptMessage:
    """Generates a user message requesting code generation."""
    content = f"Write a {language} function that performs the following task: {task_description}"
    return PromptMessage(role="user", content=TextContent(type="text", text=content))
Key Concepts:

- **Name**: By default, the prompt name is taken from the function name.
- **Parameters**: The function parameters define the inputs needed to generate the prompt.
- **Inferred Metadata**: By default:
    - **Prompt Name**: Taken from the function name (ask_about_topic).