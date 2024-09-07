# FluentLM

## Description
FluentLM is a fluent interface for language models, allowing you to chain operations in a way that feels familiar to Pandas users. It's designed for ease of use and rapid prototyping, making it a great choice for quick experimentation. This package is currently in Alpha, so expect limited error handling and potential bugs.

## Installation
To install FluentLM, simply run:

```bash
pip install mypackage
```

## Quickstart

### Calling a language model
FluentLM makes it easy to call language models. The `call_model()` function defaults to a pre-configured model and a sample message of "Hello, my friend." This provides a simple way to verify that everything is set up correctly.

By default, the model provider is Anthropic, and the model is Claude Sonnet 3.5. FluentLM retrieves your API key from environment variables. You can easily modify the provider, model, or API key location using built-in configuration functions (see the instructions below). These updates are persistent and will be applied the next time you use the package.

```python
import FluentLM as flm
 
flm.call_model()
```

You can also pass a custom message to the default model:
```python
flm.call_model("How far away is the sun?")
```

If you only specify a model provider, FluentLM will use the provider's default model. You can change the default model for each provider using configuration functions.
```python
flm.call_model("openai", "Could a gorilla play guitar?")  
```

You can also specify both the model provider and model name:
```python
flm.call_model("openai", "gpt-4o-mini", "Are there bears on Mt. Everest?")
```

FluentLM is forgiving with model names. For example, to call `gpt-4o-mini`, you can use the nickname `mini`. Therefore, the following three calls are equivalent:

```python
flm.call_model("openai", "gpt-4o-mini", "Is a sparkleberry a fruit?") # Full provider and model name
flm.call_model("openai", "mini", "Is a sparkleberry a fruit?") # Full provider name with model nickname
flm.call_model("mini", "Is a sparkleberry a fruit?") # Only model nickname
```

### Intelligent argument parsing
FluentLM intelligently parses input, automatically applying default values when arguments or argument keywords aren’t provided. Additionally, the order of arguments doesn’t matter. The main arguments are `provider_name`, `model_name`, `prompt`. Only the `prompt` argument is required, but the `prompt` keyword itself is optional. The following three calls are equivalent:

```python
flm.call_model("openai", "mini", "Why does my kitchen have german cockroaches?")
flm.call_model("Why does my kitchen have german cockroaches?", "mini", "openai")
flm.call_model(provider_name="openai", model_name="mini", prompt="Why does my kitchen have german cockroaches?")
```

