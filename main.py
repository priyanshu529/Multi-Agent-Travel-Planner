# this main.py file is for backend testing before actually implementing the streamlit code
import uuid

from langchain_core.messages import HumanMessage

from graph import app

if __name__ == "__main__":
    user_id = str(uuid.uuid4())
    config = {
        "configurable": {
            "thread_id": user_id,
        }
    }
    while(True):
        user_input = input("enter travel request:")

        result = app.invoke(
            {
                "messages": [
                    HumanMessage(content=user_input)
                ],
                "user_query": user_input,
                "flight_result": "",
                "hotel_results": "",
                "weather_result": "",
                "itinerary": "",
                "final_result": "",
                "evaluation": {},
                "llm_calls": 0,
                "max_iteration": 3,
                "revision_count": 0
            },
            config=config
        )
        from agents.input_guardrail import InputGuardrail  

        last_msg = result["messages"][-1]

        if isinstance(last_msg, InputGuardrail):
            print(last_msg.reason)
        else:
            print(last_msg.content)

        exit=input("do you want to exit:(y/n)")
        if(exit=="y"):
            break
