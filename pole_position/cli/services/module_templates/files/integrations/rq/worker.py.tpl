from {{package_name}}.integrations.rq.factory import build_rq_worker


def run_worker(*, queue_names: list[str] | None = None, burst: bool = False) -> bool:
    worker = build_rq_worker(queue_names=queue_names)
    return bool(worker.work(burst=burst))
