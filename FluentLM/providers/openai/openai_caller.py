from ...interfaces.abstract_model_caller import AbstractModelCaller

class OpenAICaller(AbstractModelCaller):
    @classmethod
    def call_model(cls, model_name, prompt, client, **kwargs):
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            result = completion.choices[0].message.content
            return result
        except Exception as e:
            print(f"Error calling API: {str(e)}")
            raise