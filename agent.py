from typing import List, Union, Optional, Dict, Any, cast
from pydantic import BaseModel, Field
from instructor import OpenAISchema
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionToolParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionMessageParam
)

SEARCH_SCHEMA = {
    "name": "search_products",
    "description": "Search for products using keywords",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Keywords to search for"
            }
        },
        "required": ["keywords"]
    }
}

PRODUCT_DETAILS_SCHEMA = {
    "name": "get_product_details",
    "description": "Get detailed information about a specific product",
    "parameters": {
        "type": "object",
        "properties": {
            "product_id": {
                "type": "string",
                "description": "Product ID to get details for"
            }
        },
        "required": ["product_id"]
    }
}

CLARIFY_SCHEMA = {
    "name": "clarify_request",
    "description": "Ask user for clarification when request is unclear",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "Question to ask user for clarification"
            }
        },
        "required": ["question"]
    }
}

SYSTEM_PROMPT = """You are a shopping assistant. Use these functions:
1. search_products: When user wants to find products (e.g., "show me shirts")
2. get_product_details: When user asks about a specific product ID (e.g., "tell me about product p1")
3. clarify_request: When user's request is unclear"""


class SearchClient:
    
    def search(self, keywords: List[str]) -> List[dict]:
        # Simulate a search operation
        return [{"id": "p1", "name": "Product 1"}, {"id": "p2", "name": "Product 2"}]

    def get_product_details(self, product_id: str) -> dict:
        # Simulate fetching product details
        return {"id": product_id, "name": f"Product {product_id}", "price": 19.99, "description": "A great product."}

class BaseAction(BaseModel):
    def execute(self) -> str:
        return ""

class Search(BaseAction):
    keywords: List[str]

    def execute(self) -> str:
        results = SearchClient().search(self.keywords)
        if not results:
            return "Sorry I couldn't find any products for your search."
        
        products = [f"{p['name']} (ID: {p['id']})" for p in results]
        return f"Here are the products I found: {', '.join(products)}"

class GetProductDetails(BaseAction):
    product_id: str

    def execute(self) -> str:
        product = SearchClient().get_product_details(self.product_id)
        if not product:
            return f"Product {self.product_id} not found"
        
        return f"{product['name']}: price: ${product['price']} - {product['description']}"

class Clarify(BaseAction):
    question: str

    def execute(self) -> str:
        return self.question

class NextActionResponse(OpenAISchema):
    next_action: Union[Search, GetProductDetails, Clarify] = Field(
        description="The next action for agent to take.")


class ShoppingAgent:
    def __init__(self):
        import os
        api_key = os.environ.get("OPENROUTER_API_KEY")
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="api_key")

    def run(self, user_message: str, conversation_history: List[Dict[str, str]] = []) -> str:
        if self.is_intent_malicious(user_message):
            return "Sorry! I cannot process this request."

        try:
            action = self.decide_next_action(user_message, conversation_history)
            if action:
                return action.execute()
            return "I'm not sure how to respond to that."
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

    def decide_next_action(self, user_message: str, conversation_history: List[Dict[str, str]]) -> Optional[BaseAction]:
        # Prepare messages with proper typing
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": SYSTEM_PROMPT} 
        ]
        
        # Add conversation history with proper typing
        for msg in conversation_history:
            if msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                messages.append({"role": "assistant", "content": msg["content"]})
            elif msg["role"] == "system":
                messages.append({"role": "system", "content": msg["content"]})
        
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        # Prepare tools with proper typing
        tools: List[ChatCompletionToolParam] = [
            {
                "type": "function",
                "function": {
                    "name": SEARCH_SCHEMA["name"],
                    "description": SEARCH_SCHEMA["description"],
                    "parameters": SEARCH_SCHEMA["parameters"]
                }
            },
            {
                "type": "function",
                "function": {
                    "name": PRODUCT_DETAILS_SCHEMA["name"],
                    "description": PRODUCT_DETAILS_SCHEMA["description"],
                    "parameters": PRODUCT_DETAILS_SCHEMA["parameters"]
                }
            },
            {
                "type": "function",
                "function": {
                    "name": CLARIFY_SCHEMA["name"],
                    "description": CLARIFY_SCHEMA["description"],
                    "parameters": CLARIFY_SCHEMA["parameters"]
                }
            }
        ]
        
        # Make the API call
        response = self.client.chat.completions.create(
            model="openai/gpt-4",
            messages=messages,
            tools=tools
        )
        
        # Check if there's a tool call
        if not response.choices or not response.choices[0].message.tool_calls:
            return None
            
        tool_call = response.choices[0].message.tool_calls[0]
        if not tool_call.function or not tool_call.function.arguments:
            return None
            
        # Parse the function arguments (safely, without eval)
        import json
        try:
            function_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            return None
        
        # Return the appropriate action
        if tool_call.function.name == "search_products":
            return Search(**function_args)
        elif tool_call.function.name == "get_product_details":
            return GetProductDetails(**function_args)
        elif tool_call.function.name == "clarify_request":
            return Clarify(**function_args)
        
        return None

    def is_intent_malicious(self, message: str) -> bool:
        return False


def main():
    agent = ShoppingAgent()
    conversation_history = []
    
    print("Shopping Assistant: Hello! How can I help you today? (Type 'bye' to exit)")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == "bye":
            print("Shopping Assistant: Goodbye! Have a nice day!")
            break
        
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Get response from agent
        response = agent.run(user_input, conversation_history)
        print(f"Shopping Assistant: {response}")
        
        # Add assistant response to conversation history
        conversation_history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()



