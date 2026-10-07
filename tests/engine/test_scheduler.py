"""Tests del scheduler del agente."""

from engine.runtime.scheduler import Priority, Scheduler, Task


def test_create_task():
    s = Scheduler()
    t = s.create("Tarea 1", "action_a")
    assert t.id.startswith("task_")
    assert t.status == "pending"
    assert t.priority == Priority.NORMAL


def test_next_task_returns_highest_priority():
    s = Scheduler()
    s.create("Low", "a", priority=Priority.LOW)
    s.create("Critical", "b", priority=Priority.CRITICAL)
    s.create("Normal", "c", priority=Priority.NORMAL)
    nxt = s.next_task()
    assert nxt.name == "Critical"


def test_next_task_respects_dependencies():
    s = Scheduler()
    t1 = s.create("Dep", "a")
    t2 = s.create("Main", "b", depends_on=[t1.id])
    nxt = s.next_task()
    assert nxt.id == t1.id
    s.mark_done(t1.id)
    nxt = s.next_task()
    assert nxt.id == t2.id


def test_mark_done():
    s = Scheduler()
    t = s.create("Test", "a")
    s.mark_running(t.id)
    s.mark_done(t.id, result="ok")
    assert t.status == "done"
    assert t.result == "ok"


def test_mark_failed():
    s = Scheduler()
    t = s.create("Test", "a")
    s.mark_failed(t.id, "error")
    assert t.status == "failed"
    assert t.error == "error"


def test_is_complete():
    s = Scheduler()
    t = s.create("Test", "a")
    assert not s.is_complete()
    s.mark_done(t.id)
    assert s.is_complete()
