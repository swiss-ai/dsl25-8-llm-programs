from dotenv import load_dotenv
import os
import time
import random
import re

import google.generativeai as genai


class Gemini():
    def __init__(self, model_name="gemini-2.0-flash", rpm=15):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Make a .env file with GEMINI_API_KEY=...")
        self.model = genai.GenerativeModel(model_name)
        self.rpm = rpm
        self.llm_calls = 0
        genai.configure(api_key=api_key)

    
    def __call__(self, prompt, depth=1):
        self.llm_calls += 1
        timeout = 60 / self.rpm + 1 + random.random()
        try:
            time.sleep(timeout / 2 + 1)
            response = self.model.generate_content(prompt)
            time.sleep(timeout / 2 + 1)
            assert response.text
            return response.text
        except Exception as e:
            time.sleep(timeout * depth)
            err_msg = str(e)
            print(" "*(depth-1) + f"ERR: {err_msg.replace('\n', '   ')}")
            if response.prompt_feedback:
                print(" "*(depth-1) + f"FEEDBACK: {response.prompt_feedback}")
            if not response.candidates:
                return ""
            if "429" in err_msg:
                match = re.search(r'seconds:\s*(\d+)', err_msg)
                if match:
                    n_secs = int(match.group(1))
                    print(" "*(depth-1) + f"sleeping for {n_secs} seconds")
                    time.sleep(n_secs + 1)
            
            return self.__call__(prompt, depth=depth+1)



