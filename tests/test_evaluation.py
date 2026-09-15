"""Unit & Integration tests for Evaluation & Benchmark Suite (Phase 12)."""

import pytest
import httpx
from app.main import app
from app.models.database import init_db
from app.config import get_settings
from app.evaluation.evaluator import compute_metrics, load_benchmark_dataset, run_benchmark_evaluation


def test_compute_metrics_math():
    """Verify precision, recall, f1, and confusion matrix arithmetic."""
    actual = ["LIKELY_TRUE", "LIKELY_TRUE", "LIKELY_FALSE", "SUSPICIOUS", "UNVERIFIED"]
    predicted = ["LIKELY_TRUE", "LIKELY_FALSE", "LIKELY_FALSE", "SUSPICIOUS", "UNVERIFIED"]

    res = compute_metrics(actual, predicted)
    assert res["total_samples"] == 5
    # 4 correct out of 5 = 80.0% accuracy
    assert res["accuracy"] == 80.0
    assert "confusion_matrix" in res
    assert res["confusion_matrix"]["LIKELY_TRUE"]["LIKELY_TRUE"] == 1
    assert res["confusion_matrix"]["LIKELY_TRUE"]["LIKELY_FALSE"] == 1
    assert res["macro_f1"] > 0


def test_benchmark_dataset_loaded():
    """Verify curated ground-truth dataset contains all 4 classes."""
    data = load_benchmark_dataset()
    assert len(data) >= 15
    classes = {d["expected_verdict"] for d in data}
    assert "LIKELY_TRUE" in classes
    assert "LIKELY_FALSE" in classes
    assert "SUSPICIOUS" in classes
    assert "UNVERIFIED" in classes


@pytest.mark.asyncio
async def test_api_evaluation_metrics():
    """Verify GET /api/evaluation/metrics endpoint returns full performance suite."""
    settings = get_settings()
    await init_db(settings.database_url)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/evaluation/metrics")
        assert resp.status_code == 200
        data = resp.json()

        assert "metrics" in data
        assert "accuracy" in data["metrics"]
        assert "macro_f1" in data["metrics"]
        assert "macro_precision" in data["metrics"]
        assert "macro_recall" in data["metrics"]
        assert "confusion_matrix" in data["metrics"]
        assert "per_class" in data["metrics"]
