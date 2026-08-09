import json
import urllib.request
import time


BASE_URL = "http://127.0.0.1:8000/api/interview"

SESSION_ID = "full-e2e-test-004"


answers = [
    "Embeddings represent text as vectors so that semantically similar content can be located near each other in vector space.",

    "I would compare the embedding model based on retrieval quality, latency, dimensionality, and the quality of results on representative queries.",

    "For retrieval I would generate a query embedding, search the vector index, retrieve the most relevant chunks, and pass the selected context to the language model.",

    "For prompt engineering I would compare different prompt versions using a fixed evaluation set and measure accuracy, compliance, consistency, and response quality.",

    "For a production RAG system I would separate retrieval from generation and monitor retrieval quality, latency, failures, token usage, and model responses.",

    "For agents I would define clear responsibilities and tool boundaries, and I would use orchestration when a task requires multiple specialized steps.",

    "I would expose tools through controlled interfaces and make sure the model only has access to the tools and data required for the task.",

    "For production deployment I would add logging, metrics, health checks, error handling, monitoring, and alerting so failures can be detected and diagnosed.",
]


# =========================================================
# HTTP POST HELPER
# =========================================================

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


# =========================================================
# PRINT HEADER
# =========================================================

print("=" * 70)
print("FULL PS2 END-TO-END INTERVIEW TEST")
print("=" * 70)


# =========================================================
# FIRST REQUEST
# =========================================================

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

print(f"\nDONE: {response['done']}")


# =========================================================
# FOLLOW-UP REQUESTS
# =========================================================

for answer in answers:

    print(
        "\n⏱ Waiting 30 seconds before the next interview turn..."
    )

    time.sleep(30)


    # -----------------------------------------------------
    # SEND CANDIDATE ANSWER
    # -----------------------------------------------------

    response = post({
        "sessionId": SESSION_ID,
        "message": answer
    })


    # -----------------------------------------------------
    # CHECK IF INTERVIEW IS COMPLETE
    # -----------------------------------------------------
    #
    # IMPORTANT:
    #
    # When the candidate answers Question 8,
    # the backend returns:
    #
    # done = True
    #
    # That response contains FINAL FEEDBACK,
    # not Question 9.
    #
    # Therefore we handle it BEFORE incrementing
    # question_number.
    # -----------------------------------------------------

    if response.get("done"):

        print("\n" + "=" * 70)
        print("INTERVIEW COMPLETE")
        print("=" * 70)

        print("\nDONE: True")


        # -------------------------------------------------
        # FINAL FEEDBACK
        # -------------------------------------------------

        if response.get("feedback"):

            print("\nFINAL FEEDBACK")
            print("=" * 70)

            feedback = response["feedback"]


            # ---------------------------------------------
            # SUMMARY
            # ---------------------------------------------

            print("\nSUMMARY:")
            print(feedback["summary"])


            # ---------------------------------------------
            # STRENGTHS
            # ---------------------------------------------

            print("\nSTRENGTHS:")

            for item in feedback["strengths"]:

                print(f"- {item}")


            # ---------------------------------------------
            # GAPS
            # ---------------------------------------------

            print("\nGAPS:")

            for item in feedback["gaps"]:

                print(f"- {item}")


            # ---------------------------------------------
            # NEXT STEPS
            # ---------------------------------------------

            print("\nNEXT STEPS:")

            for item in feedback["next"]:

                print(f"- {item}")


        # -------------------------------------------------
        # STOP LOOP
        # -------------------------------------------------

        break


    # -----------------------------------------------------
    # A NEW INTERVIEW QUESTION WAS RETURNED
    # -----------------------------------------------------

    question_number += 1


    print(
        f"\nQUESTION {question_number}"
    )

    print("-" * 70)

    print(
        response["reply"]
    )

    print(
        f"\nDONE: {response['done']}"
    )


# =========================================================
# END
# =========================================================

print("\n" + "=" * 70)
print("END-TO-END TEST FINISHED")
print("=" * 70)