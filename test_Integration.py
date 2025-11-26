import pytest
from main import app
from fastapi.testclient import TestClient
client=TestClient(app)
def test_missing_idempotency_key():
    tr=client.post("/give_token")
    token=tr.json().get("token")
    body={"prompt":"Joke"}
    headers={"Authorization": f"Bearer {token}"}
    response=client.post("/process",json=body ,headers=headers)
    assert response.status_code==400
    assert response.json()=={"detail":"Idempotency-key header is required"}

def test_invalid_prompt():
    tr=client.post("/give_token")
    token=tr.json().get("token")
    body={"prompt":"Unknown"}
    headers={"Idempotency-Key":"test-key-1","Authorization": f"Bearer {token}"}
    response=client.post("/process",json=body,headers=headers)
    assert response.status_code==400
    assert response.json()=={"detail":"Invalid prompt"}

def test_valid_joke_prompt():
    tr=client.post("/give_token")
    token=tr.json().get("token")
    body={"prompt":"Joke"}
    headers={"Idempotency-key":"test-key", "Authorization": f"Bearer {token}"}
    response=client.post("/process",json=body,headers=headers)
    assert response.status_code==200
    assert response.json()=={"response":"why didi the chicken cross the road? to get to the other side!"}

def test_valid_quote_prompt():
    tr=client.post("/give_token")
    token=tr.json().get("token")
    body={"prompt":"Quote"}
    headers={"Idempotency-Key":"test-key-2" ,"Authorization": f"Bearer {token}"}
    response=client.post("/process",json=body,headers=headers)
    assert response.status_code==200
    assert response.json()=={"response":"The only limit to our realization of tomorrow is our doubts of today."}

def test_idempotency_key_reuse():
    tr=client.post("/give_token")
    token=tr.json().get("token")
    body={"prompt":"Joke"}
    headers={"Idempotency-Key":"test-key-3", "Authorization": f"Bearer {token}"}
    response1=client.post("/process",json=body,headers=headers)
    response2=client.post("/process",json=body,headers=headers)
    assert response1.status_code==200
    assert response2.status_code==200
    assert response1.json()==response2.json()

def test_give_token():
    response=client.post("/give_token")
    assert response.status_code== 200
    assert "token" in response.json()

