from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time, json, random

chrome_options = Options()
chrome_options.add_argument("--log-level=3")
service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://metis.slimstampen.nl")
last_cue_text = None
cue_answers_dict = {}
neighbor_keys = {
    'a': ['q', 's', 'z'], 'b': ['v', 'g', 'h', 'n'], 'c': ['x', 'd', 'f', 'v'], 
    'd': ['s', 'e', 'f'], 'e': ['w', 'd', 'r'], 'f': ['d', 'g', 'r', 'v'], 
    'g': ['f', 'h', 't'], 'h': ['g', 'j', 'y', 'n'], 'i': ['u', 'o', 'k'], 
    'j': ['h', 'k', 'u', 'm'], 'k': ['j', 'l', 'o', 'i'], 'l': ['k', ';', 'o'], 
    'm': ['n', 'j'], 'n': ['b', 'h', 'm', 'j'], 'o': ['i', 'p', 'l'], 'p': ['o', 'l'], 
    'q': ['w', 'a'], 'r': ['e', 'd', 'f', 'j'], 's': ['a', 'd', 'x', 'z'], 
    't': ['r', 'f', 'g', 'y'], 'u': ['y', 'h', 'j', 'i'], 'v': ['c', 'f', 'g', 'b'], 
    'w': ['q', 'e', 's'], 'x': ['s', 'd', 'c'], 'y': ['t', 'h', 'u'], 'z': ['a', 's', 'x'],
}

def update_cue_answers(requests):
    for request in requests:
        try:
            response_data = json.loads(request.response.body.decode('utf-8', errors='ignore'))
            if isinstance(response_data, list):
                for item in (i for i in response_data if isinstance(i, dict)):
                    for cue in item.get("cueTexts", []):
                        if cue_answers_dict.get(cue) != item.get("answers", []):
                            cue_answers_dict[cue] = item["answers"]
                            
        except (json.JSONDecodeError, AttributeError):
            continue

while True:
    time.sleep(random.uniform(1.5, 2.25)) # Lower = Faster | Be Mindfull
    update_cue_answers(driver.requests)
    
    try:
        button = driver.find_elements(By.CSS_SELECTOR, 'ion-button[data-test="register-study-trial"]')
        
        if button:
            button[0].click()
            print(f"\n{time.strftime('[%H:%M:%S]')} Button clicked!")
            continue
        
        cue_text = driver.find_element(By.ID, "cue-text").text.strip()
        native_input = driver.find_element(By.CSS_SELECTOR, "ion-input[name='answerInput'] input.native-input")
        
        if cue_text != last_cue_text and native_input:
            answer = cue_answers_dict[cue_text]
            print(f"\n{time.strftime('[%H:%M:%S]')} {'Word:':<7} {cue_text}")
            print(f"{time.strftime('[%H:%M:%S]')} {'Answer:':<7} {answer[0]}")

            for char in answer[0]:
                if random.random() < 0.02 and neighbor_keys.get(char, []): # 2% chance of making a mistake
                    native_input.send_keys(char)
                    time.sleep(0.01)
                    native_input.send_keys(random.choice(neighbor_keys.get(char, [])))
                    time.sleep(random.uniform(0.3, 0.5))
                    native_input.send_keys(Keys.BACKSPACE)
                    time.sleep(random.uniform(0.1, 0.25))
                else:
                    native_input.send_keys(char)
                    time.sleep(random.uniform(0.01, 0.1))

            native_input.send_keys(Keys.RETURN)
            last_cue_text = cue_text

    except Exception as e:
        pass
