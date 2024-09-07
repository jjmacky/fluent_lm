from ...interfaces.abstract_model_caller import AbstractModelCaller

class AnthropicCaller(AbstractModelCaller):
    @classmethod
    def call_model(cls, model_name, prompt, client, **kwargs):
        try:
            # Adjust this based on the actual Anthropic API usage
            message = client.messages.create(
                model = model_name,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            result = message.content[0].text
            return result
        except Exception as e:
            print(f"Error calling Anthropic API: {str(e)}")
            raise
