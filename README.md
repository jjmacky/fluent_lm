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

### Chaining examples

```python
flm.PipelineBuilder().with_prompt("Hello, my freind.").call_model("openai", "gpt-4o-mini").build().execute()
```

```python
simple_pipeline = (
    flm.PipelineBuilder()
    .with_prompt("What is the capital of {location}", {"location": "France"})
    .call_model("mini")
    .build()
)

simple_result = simple_pipeline.execute()
print(simple_result)
```

```python
countries = ["France", "Germany", "United States"]

for country in countries:
    simple_pipeline = (
        flm.PipelineBuilder() 
        .with_prompt("What is the capital of {location}", {"location": country})
        .call_model("mini")
        .build()
    )
  
    simple_result = simple_pipeline.execute()
    print(simple_result)
```


```python
simple_pipeline = (
    flm.PipelineBuilder()
    .with_prompt("What is the capital of {location}", {"location": "France"})
    .call_model("mini", output_key = "location_response")
    .call_model("mini", prompt = "Is this correct? {location_response}")
    .apply(lambda text: text.upper())
    .build()
)

simple_result = simple_pipeline.execute()
print(simple_result)
```


```python
exemplar_question = "A microwave oven is connected to an outlet, 120 V, and draws a current of 2 amps. At what rate is energy being used by the microwave oven?"

exemplar_principles = """
The physics principles behind this question relate to electrical power and energy consumption. Here are the relevant principles and equations:

1. Ohm's Law: This fundamental principle relates voltage (V), current (I), and resistance (R) in an electrical circuit.
V = I * R

2. Electrical Power: The rate at which electrical energy is transferred or converted in a circuit is given by the power equation.
P = V * I
Where:
P is power in watts (W)
V is voltage in volts (V)
I is current in amperes (A)

3. Energy and Power Relationship: Energy is the capacity to do work, while power is the rate at which energy is transferred or work is done.
E = P * t
Where:
E is energy in joules (J)
P is power in watts (W)
t is time in seconds (s)

4. Unit Conversions: Understanding the relationships between different units of power and energy might be relevant.
1 kilowatt (kW) = 1000 watts (W)
1 kilowatt-hour (kWh) = 3,600,000 joules (J)

5. Conservation of Energy: The principle that energy cannot be created or destroyed, only converted from one form to another. In this case, electrical energy is being converted to other forms (primarily heat and electromagnetic waves) in the microwave oven.

These principles and equations provide the foundation for calculating the rate at which energy is being used by an electrical appliance given its voltage and current draw.
"""

exemplar_solution = """
Let's solve this problem step by step using the principles.

Given:
- Voltage (V) = 120 V
- Current (I) = 2 A

We need to find the rate at which energy is being used, which is equivalent to the power consumed by the microwave oven.

Step 1: Use the electrical power equation to calculate the power.
P = V * I
P = 120 V * 2 A
P = 240 W

Therefore, the microwave oven is using energy at a rate of 240 watts.

To express this in kilowatts, we can convert:
240 W = 0.24 kW

Conclusion: The microwave oven is using energy at a rate of 240 watts or 0.24 kilowatts.
"""

initial_context = {"exemplar_question": exemplar_question, "exemplar_principles": exemplar_principles, "exemplar_solution": exemplar_solution}

# questions_dataset = {
#     "question 1": "A pipe full of air is closed at one end. A standing wave is produced in the pipe, causing the pipe to sound a note. Which of the following is a correct statement about the wave’s properties at the closed end of the pipe?",
#     "question 2": "A photocell of work function ϕ = 2eV is connected to a resistor in series. Light of frequency f = 1 × 10^15 Hz hits a metal plate of the photocell. If the power of the light is P = 100 W, what is the current through the resistor?"
# }

questions_dataset = [
   "A pipe full of air is closed at one end. A standing wave is produced in the pipe, causing the pipe to sound a note. Which of the following is a correct statement about the wave’s properties at the closed end of the pipe?",
   "A photocell of work function ϕ = 2eV is connected to a resistor in series. Light of frequency f = 1 × 10^15 Hz hits a metal plate of the photocell. If the power of the light is P = 100 W, what is the current through the resistor?"
]


from datasets import load_dataset
physics_dataset_examples = load_dataset("lukaemon/mmlu", "high_school_physics", split="train")
subset = physics_dataset_examples.select(range(1, 5))

pipeline = (
    flm.PipelineBuilder()
    .using_dataset(subset, input_key="input", output_key="question", target="target", target_type="indirect")
    .with_prompt(
        """You are an expert at Physics. You are given a Physics problem.
        Your task is to extract the Physics concepts and principles involved in solving the problem.
        Here is an example:\n
        --- Example ----\n
        Question: {exemplar_question}\n
        Principles:{exemplar_principles}\n
        --- End of Example ----\n\n
        Question: {question}\n
        Do not solve the problem. Only detail the principles and equations involved.\n
        Principles Involved:""",
        variables={
            "exemplar_question": exemplar_question,
            "exemplar_principles": exemplar_principles
        },
        output_key="principles_prompt"
    )
    .call_model("mini", input_key="principles_prompt", output_key="principles")
    .with_prompt(
        """You are an expert at Physics.
        You are given a Physics problem and a set of principles involved in solving the problem.
        Solve the problem step by step by following the principles.
        Here is an example:\n
        --- Example ----\n
        Question: {exemplar_question}\n
        Principles: {exemplar_principles}\n
        Solution: {exemplar_solution}\n
        --- End of Example ----\n\n
        Question: {question}\n 
        Principles Involved: {principles}\n
        Solution:""",
        variables={
            "exemplar_question": exemplar_question,
            "exemplar_principles": exemplar_principles,
            "exemplar_solution": exemplar_solution
        },
        output_key="solution_prompt"
    )
    #.call_model("openai", "gpt-4o-mini", input_key="solution_prompt")
    .call_model("mini", output_key="physics_solution")
    .call_model("sonnet", prompt="Does this solution: '{physics_solution}' match the correct solution: '{target}'?")
    .build()
)

results = pipeline.execute() 
print(results)
```