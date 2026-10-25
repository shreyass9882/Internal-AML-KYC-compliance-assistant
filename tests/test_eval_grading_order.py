"""Evaluation answers every question before grading any, so the judge model never swaps in between answers."""
import json


def test_all_answers_come_before_any_grading(built_cfg, monkeypatch):
    import amlrag.eval.runner as runner
    from amlrag.pipeline import Assistant

    events: list[str] = []
    real_ask = Assistant.ask

    def ask(self, mode, query):
        events.append("answer")
        return real_ask(self, mode, query)

    class FakeJudge:
        name = "fake-judge"

        def __init__(self, llm, cache_path=None):
            pass

        def supported(self, claim, passages, scenario=None):
            events.append("grade")
            return True

        def save(self):
            events.append("save")

    monkeypatch.setattr(Assistant, "ask", ask)
    monkeypatch.setattr(runner, "make_judge", lambda cfg: object())
    monkeypatch.setattr(runner, "Judge", FakeJudge)

    out, metrics = runner.run_eval(built_cfg, verbose=False, limit=6)

    assert events.count("answer") == 6 and "grade" in events
    last_answer = max(i for i, e in enumerate(events) if e == "answer")
    first_grade = events.index("grade")
    assert last_answer < first_grade, "grading started before all questions were answered"
    assert events[-1] == "save"

    answers = [json.loads(l) for l in (out / "answers.jsonl").read_text().splitlines()]
    preds = [json.loads(l) for l in (out / "predictions.jsonl").read_text().splitlines()]
    assert [a["id"] for a in answers] == [p["id"] for p in preds]
    assert all(p["judge_name"] == "fake-judge" for p in preds)
    run = json.loads((out / "metrics.json").read_text())["run"]
    assert run["grading"] == "after all answers" and run["answer_phase_s"] >= 0 and run["grading_phase_s"] >= 0
    assert "then grading" in (out / "report.md").read_text()


def test_a_failed_answer_is_reported_not_graded(built_cfg, monkeypatch):
    import amlrag.eval.runner as runner
    from amlrag.pipeline import Assistant

    def boom(self, mode, query):
        raise RuntimeError("model crashed")

    monkeypatch.setattr(Assistant, "ask", boom)
    out, _ = runner.run_eval(built_cfg, verbose=False, limit=2)
    preds = [json.loads(l) for l in (out / "predictions.jsonl").read_text().splitlines()]
    assert all(p["error"] == "model crashed" and p["abstained"] and p["tier"] is None for p in preds)
