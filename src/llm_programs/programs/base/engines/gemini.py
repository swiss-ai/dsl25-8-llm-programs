from llm_programs.utils import printw, debug_panel

from dotenv import load_dotenv
import os
import time
import random
import re
import logging

import google.generativeai as genai

logger = logging.getLogger('rich')

class Gemini():
    def __init__(self, model_name="gemini-2.0-flash", rpm=15, debug=False):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Make a .env file with GEMINI_API_KEY=...")
        self.model = genai.GenerativeModel(model_name)
        self.rpm = rpm
        self.n_calls = 0
        self.n_in_chars = 0
        self.n_out_chars = 0
        self.debug = debug
        genai.configure(api_key=api_key)

    
    def __call__(self, prompt: str, depth=1) -> str:
        timeout = 60 / self.rpm + random.random()
        if self.debug and depth == 1:
            debug_panel(logger, "Prompt", prompt)
            logger.debug(f"{self.n_calls} calls to LLM so far, timeout = {timeout:.2f} seconds")
        try:
            time.sleep(timeout / 2 + .5)
            response = self.model.generate_content(prompt)
            time.sleep(timeout / 2 + .5)
            if not response.candidates:
                print(" "*(depth-1) + f"WARN: no candidates")
                return ""
            assert response.text
            self.n_calls += 1
            self.n_in_chars += len(prompt)
            self.n_out_chars += len(response.text)
            if self.debug and depth == 1:
                debug_panel(logger, "Response", response.text)
            return response.text
        except Exception as e:
            err_msg = str(e)
            print(" "*(depth-1) + f"ERR: {err_msg.replace('\n', '   ')}")
            if "429" in err_msg:
                match = re.search(r'seconds:\s*(\d+)', err_msg)
                if match:
                    n_secs = int(match.group(1))
                    print(" "*(depth-1) + f"sleeping for {n_secs} seconds")
                    time.sleep(n_secs + 1)
            else:
                time.sleep(timeout * depth)
            return self.__call__(prompt, depth=depth+1)
 

    @property
    def counters(self):
        return (self.n_calls, self.n_in_chars, self.n_out_chars)

