import os
import sys
import traceback
from dotenv import load_dotenv

load_dotenv()

def main():
    try:
        from openai import OpenAI
    except Exception as e:
        print("OpenAI client not installed:", e)
        return 2

    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("NVIDIA_API_KEY not set in environment. Set it and retry.")
        return 3

    proxy = os.getenv("NVIDIA_PROXY")
    if proxy:
        os.environ.setdefault("HTTP_PROXY", proxy)
        os.environ.setdefault("HTTPS_PROXY", proxy)
        os.environ.setdefault("ALL_PROXY", proxy)
        print("Using NVIDIA_PROXY for outbound requests")

    client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)

    try:
        completion = client.chat.completions.create(
            model="nvidia/nemotron-3-ultra-550b-a55b",
            messages=[{"role": "user", "content": "Write a limerick about the wonders of GPU computing."}],
            temperature=1,
            top_p=0.95,
            max_tokens=256,
            extra_body={"chat_template_kwargs": {"enable_thinking": True}},
            stream=True,
        )

        for chunk in completion:
            if not getattr(chunk, "choices", None):
                continue
            reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
            if reasoning:
                print(reasoning, end="")
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
        print()
        return 0
    except Exception as e:
        print("Call failed:")
        traceback.print_exc(limit=2)
        return 4


if __name__ == "__main__":
    sys.exit(main())
