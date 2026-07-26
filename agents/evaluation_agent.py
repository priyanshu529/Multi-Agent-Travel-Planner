from model import TravelState, EvaluationResult
from llm import llm


def evaluation_agent(state: TravelState):
    evaluation_llm = llm.with_structured_output(EvaluationResult)
    prompt = f"""
You are a senior travel QA reviewer.

Review the travel plan below.

Check:

1. Flight prices realistic
2. Flight dates valid
3. Hotel exists
4. Hotel price reasonable
5. Budget respected
6. Itinerary realistic
7. Internal consistency
8. No impossible timings

Travel Plan:

{state["final_result"]}
If the travel plan is realistic and internally consistent,
return passed=True.

If there is any significant issue (incorrect pricing,
invalid dates, impossible itinerary, budget violation,
or nonexistent hotel), return passed=False.

Be strict.

Return ONLY the structured output.
"""
    result = evaluation_llm.invoke(prompt)
    return {
        "evaluation": result.model_dump(),
        "revision_count": state.get("revision_count", 0) + 1
    }


def evaluation_router(state: TravelState):
    evaluation = state["evaluation"]
    if evaluation["passed"] and evaluation["confidence"] >= 0.85:
        return "approved"
    if state["revision_count"] >= state["max_iteration"]:
        return "approved"
    return "revise"