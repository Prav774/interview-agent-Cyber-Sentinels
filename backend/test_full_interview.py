import json
import urllib.request


BASE_URL = "http://127.0.0.1:8000/api/interview"

SESSION_ID = "full-e2e-test-002"

answers = [
    "Embeddings represent text as vectors so that semantically similar content can be located near each other in vector space.",

    "I would compare the embedding model based on retrieval quality, latency, dimensionality, and the quality of results on representative queries.",

    "For retrieval I would generate a query embedding, search the vector index, retrieve the most relevant chunks, and pass the selected context to the language model.",

    "For prompt engineering I would compare different prompt versions using a fixed evaluation set and measure accuracy, compliance, consistency, and response quality.",

    "For a production RAG system I would separate retrieval from generation and monitor retrieval quality, latency, failures, token usage, and model responses.",

    "For agents I would define clear responsibilities and tool boundaries, and I would use orchestration when a task requires multiple specialized steps.",

    "I would expose tools through controlled interfaces and make sure the model only has access to the tools and data required for the task.",

    "For production deployment I would add logging, metrics, health checks, error handling, monitoring, and alerting so failures can be detected and diagnosed."
]


def post(payload):
    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        BASE_URL,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        body = response.read().decode("utf-8")

    return json.loads(body)


print("=" * 70)
print("FULL PS2 END-TO-END INTERVIEW TEST")
print("=" * 70)

# ------------------------------------------------------------
# FIRST REQUEST
# ------------------------------------------------------------

response = post({
    "sessionId": SESSION_ID,
    "candidate": {
        "member": {
            "id": "CAND-001"
        }
    }
})

question_number = 1

print(f"\nQUESTION {question_number}")
print("-" * 70)
print(response["reply"])

# ------------------------------------------------------------
# FOLLOW-UP REQUESTS
# ------------------------------------------------------------

for answer in answers:

    response = post({
        "sessionId": SESSION_ID,
        "message": answer
    })

    question_number += 1

    print(f"\nQUESTION {question_number}")
    print("-" * 70)
    print(response["reply"])

    print(f"\nDONE: {response['done']}")

    if response.get("feedback"):
        print("\nFINAL FEEDBACK")
        print("=" * 70)

        feedback = response["feedback"]

        print("\nSUMMARY:")
        print(feedback["summary"])

        print("\nSTRENGTHS:")
        for item in feedback["strengths"]:
            print(f"- {item}")

        print("\nGAPS:")
        for item in feedback["gaps"]:
            print(f"- {item}")

        print("\nNEXT STEPS:")
        for item in feedback["next"]:
            print(f"- {item}")

        break


print("\n" + "=" * 70)
print("END-TO-END TEST FINISHED")
print("=" * 70)