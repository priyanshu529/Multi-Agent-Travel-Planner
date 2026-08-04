from model import TravelState

def route_input_guardrail(state: TravelState):
    if state.get("input_rejected") is True:
        return "rejected"
    else:
        return "approved"
