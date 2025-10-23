#import openai
import re
import argparse
from pythonAPI import *
import math
import numpy as np
import os
import json
import time
      
import asyncio
import base64
import json
import websockets
import pyaudio
from configure import auth_key

def transcribe_audio(duration=30):
    FRAMES_PER_BUFFER = 3200
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    p = pyaudio.PyAudio()

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER
    )

    URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"
    transcribed_text = []

    async def send_receive():
        async with websockets.connect(
            URL,
            extra_headers=(("Authorization", "a73502a363ad4c3eb2bfe4647ad6a61e"),),
            ping_interval=5,
            ping_timeout=20
        ) as ws:

            await asyncio.sleep(0.1)

            async def send():
                while True:
                    try:
                        data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                        data = base64.b64encode(data).decode("utf-8")
                        json_data = json.dumps({"audio_data": str(data)})
                        await ws.send(json_data)
                    except websockets.exceptions.ConnectionClosedError:
                        break
                    except Exception:
                        break
                    await asyncio.sleep(0.01)

            async def receive():
                nonlocal transcribed_text
                while True:
                    try:
                        result_str = await ws.recv()
                        result_json = json.loads(result_str)
                        if result_json['message_type'] == 'FinalTranscript':
                            transcribed_text.append(result_json['text'])
                    except websockets.exceptions.ConnectionClosedError:
                        break
                    except Exception:
                        break

            sender = asyncio.create_task(send())
            receiver = asyncio.create_task(receive())

            await asyncio.sleep(duration)
            sender.cancel()
            receiver.cancel()

    asyncio.run(send_receive())

    stream.stop_stream()
    stream.close()
    p.terminate()

    return " ".join(transcribed_text)


parser = argparse.ArgumentParser()
parser.add_argument("--prompt", type=str, default="prompts/airsim_basic.txt")
parser.add_argument("--sysprompt", type=str, default="prompts/airsim_basic.txt")
args = parser.parse_args()

with open("config.json", "r") as f:
    config = json.load(f)

print("Initializing ChatGPT...")
openai.api_key = config["OPENAI_API_KEY"]

with open(args.sysprompt, "r") as f:
    sysprompt = f.read()

chat_history = [
    {
        "role": "system",
        "content": sysprompt
    },
    {
        "role": "user",
        "content": "move 10 units up"
    },
    {
        "role": "assistant",
        "content": "Here's how you might command an agent to move up in a virtual environment."
    }
]


def ask(prompt):
    chat_history.append(
        {
            "role": "user",
            "content": prompt,   
        }
    )
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chat_history,
        temperature=0
    )
    chat_history.append(
        {
            "role": "assistant",
            "content": completion.choices[0].message.content,
        }
    )
    return chat_history[-1]["content"]


print(f"Done.")

code_block_regex = re.compile(r"```(.*?)```", re.DOTALL)


def extract_python_code(content):
    code_blocks = code_block_regex.findall(content)
    if code_blocks:
        full_code = "\n".join(code_blocks)

        if full_code.startswith("python"):
            full_code = full_code[7:]

        return full_code
    else:
        return None


class colors:  # You may need to change color settings
    RED = "\033[31m"
    ENDC = "\033[m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"


print("System initialized.")

with open(args.prompt, "r") as f:
    prompt = f.read()

ask(prompt)
print("Welcome to the interactive system! I am ready to help you with your questions and commands.")

question = transcribe_audio(duration=5)
print(f"Transcribed request: {question}")



response = ask(question)
print(f"\n{response}\n")

code = extract_python_code(response)
if code is not None:
    print("Here's the code you can use:")
    print(code)
