import requests


def promt_function(UseCase, technical_requirement):
    promt = f'''
        Compare the information in the two provided texts ({UseCase}) and ({technical_requirement}): 
        1. If both texts convey the same information, respond with "All is correct." 
        2. If the texts contain conflicting information, provide a comment on what is incorrect. 
        3. If the texts are unrelated, respond with "Not related." 
        
        
        **Example Comparisons:** 
        
        1. **Text 1:** ("Electrified vehicle" means a vehicle with a powertrain containing at least one electric motor or electric motor-generator.) **Text 2:** (A vehicle with a powertrain containing 2 electric motor-generators.) **Response:** All is correct. 
        
        2. **Text 1:** ("Electrified vehicle" means a vehicle with a powertrain containing at least one electric motor or electric motor-generator.) **Text 2:** (A vehicle with a powertrain containing 2 diesel motors.) **Response:** No, an electrified vehicle must contain at least one electric motor or electric motor-generator. 
        
        3. **Text 1:** (The test speeds for approval are 10 km/h and 20 km/h.) **Text 2:** (The test speed is 15 km per hour.) **Response:** All is correct. 
        
        4. **Text 1:** (The test speeds for approval are 10 km/h and 20 km/h.) **Text 2:** (The test speed is 30 km per hour.) **Response:** No, the test speed must be 10 km/h and 20 km/h. 
        
        5. **Text 1:** ("Frequency Shift" means the variation of the frequency content of the AVAS sound as a function of the vehicle speed.) **Text 2:** ("Frequency Shift" means a vehicle with a powertrain containing at least one electric motor or electric motor-generator.) **Response:** No, "Frequency Shift" refers to the variation of the frequency content of the AVAS sound as a function of the vehicle speed. 
        
        6. **Text 1:** ("Electrified vehicle" means a vehicle with a powertrain containing at least one electric motor or electric motor-generator.) **Text 2:** (A vehicle with a powertrain containing 2 electric motor-generators.) **Response:** All is correct. 
        
        7. **Text 1:** ("Electrified vehicle" means a vehicle with a powertrain containing at least one electric motor or electric motor-generator.) **Text 2:** ("Hybrid Electric Vehicle" (HEV) means a vehicle with a powertrain containing at least one electric motor or electric motor generator and at least one internal combustion engine as propulsion energy converters.) **Response:** Not related.
    '''
    return promt


class GPTModel:
    def __init__(self, api_key, model="gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.endpoint = "https://gptunnel.ru/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def send_request(self, user_message):
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }

        response = requests.post(self.endpoint, headers=self.headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def generate_text(self, user_message):
        return self.send_request(user_message)["choices"][0]["message"]["content"]

    def summarize(self, user_message):
        return self.generate_text(user_message + ' summarize this text')

model = GPTModel('your_api_key')

# print(model.summarize('I want to buy flowers, i want to buy blue and fluffy, can you help me?'))
# print(model.generate_text('I want to buy flowers, i want to buy blue and fluffy, can you help me?'))
