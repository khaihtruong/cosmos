# LLM Chat

LLM Chat is a chatbot leveraging industry-standard LLM models (OpenAI, Gemini, Anthropic) to converse and capture patient's behavior in between therapy session. This would allow the clinician to have a good understand of their patient.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install necessary packages.

```bash
pip install -r requirements.txt
```

To start the program run the following command from the root of the project
```bash
python manage.py
```

## Documentation
API documentation implemented with Swagger available at /docs

## Project Structure
```bash
|-- main
|   |-- llm_chat              # backend
|       |-- models            # database model
|       |-- routes            # api routes
|       |-- services          # setup LLM interface
|       |-- utils             # role management
|       |--__init__.py
|       |--extensions.py
|   |-- client                # frontend (soon)
|   |-- templates             # frontend (current)
|   |-- manage.py             # app entry point
|   |-- README.md
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MindLamp](https://www.digitalpsych.org/mindlamp.html)