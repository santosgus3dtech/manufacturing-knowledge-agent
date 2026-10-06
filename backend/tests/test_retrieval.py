from manufacturing_agent.fixtures import load_chunks, load_evaluation_cases
from manufacturing_agent.retrieval import HybridRetriever
from manufacturing_agent.services import EvaluationService


def test_every_search_result_has_a_grounded_citation() -> None:
    retriever = HybridRetriever(load_chunks())
    response = retriever.search("PETG is stringing and popping after storage", top_k=3)

    assert response.results
    assert response.results[0].document_id == "MAT-017"
    assert response.results[0].page >= 1
    assert response.results[0].excerpt


def test_retrieval_evaluation_meets_portfolio_threshold() -> None:
    retriever = HybridRetriever(load_chunks())
    summary = EvaluationService(retriever).run()

    assert summary.cases == len(load_evaluation_cases())
    assert summary.recall_at_3 >= 0.875
    assert summary.mean_reciprocal_rank >= 0.75


def test_domain_filter_is_applied_before_ranking() -> None:
    retriever = HybridRetriever(load_chunks())
    response = retriever.search("machine evidence and recovery", domain="incident-response")

    assert response.results
    assert {result.domain for result in response.results} == {"incident-response"}
