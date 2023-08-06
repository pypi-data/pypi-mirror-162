import logging
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from . import deploy_state, exceptions, store_payload, unpack_payload, verify_payload

logger = logging.getLogger(__name__)
workers = ThreadPoolExecutor(10)


def handle_zip_in_threadpool(app, request, store_data=True, unpack_data=True):
    def fn(out: Queue):
        try:
            _handle_zip = handle_zip(app, request, store_data, unpack_data)
            for res in _handle_zip:
                out.put(res)
                logger.info(res)
        except Exception as err:
            out.put(err)
            logger.exception(err)
        out.put(StopIteration)

    out = Queue()
    workers.submit(fn, out)
    return iter(out.get, StopIteration)


def handle_zip(app, request, store_data=True, unpack_data=True):
    """
    A generator. Yields result from ``deploy_zip_sequence`` and
    updates app.config["shared_progress_dict"] with progression
    and logs.
    """
    progress = None
    _handle_zip = deploy_zip_sequence(app, request, store_data, unpack_data)

    res = next(_handle_zip)

    if isinstance(res, dict) and "root" in res and res["root"]:
        with app.config["shared_lock"]:
            progress = app.config["shared_progress_dict"][res["root"]] = {}
            log = progress["log"] = []
    yield res

    for res in _handle_zip:
        if isinstance(res, dict):
            with app.config["shared_lock"]:
                if progress:
                    progress.update(res)
        else:
            with app.config["shared_lock"]:
                if progress:
                    log.append(res)
        yield res


def deploy_zip_sequence(app, request, store_data=True, unpack_data=True):
    """
    A generator. Handle storing and unpacking of zip files.
    Yield protocol:
    - if type is str: log message.
    - if type is dict: result or progress.
    first result is a "in progress" dict with keys: progress, root
    final result is a dict with following keys: result, result_code, root
    """
    root = None
    try:
        root = request.headers.get("Root")
        result = {"root": root, "result": "In progress", "result_code": 2}

        yield {"root": root}  # first result: returns only root
        yield f"root: {root}"

        if "Root" not in request.headers:
            raise exceptions.Fail("HTTP header Root not found")

        headers = dict(request.headers)
        for header in headers.keys():
            if header.lower() == "token":
                headers[header] = "****"

        remote_info = {
            "remote_address": request.remote_addr,
            "remote_user": request.remote_user,
        }

        if store_data:
            payload = request.get_data()
            headers["Content-Length"] = request.headers.get("Content-Length", "0")

            yield "store data"
            cache_file, cache_id = store_payload.store(
                payload, app.config["cache_root"], headers, remote_info
            )

            yield from verify_payload.verify_content(
                int(headers.get("Content-Length", "0")),
                len(payload),
                cache_file.stat().st_size,
            )
            if app.config["keep_on_disk"] > 0:
                yield from store_payload.auto_delete(
                    app.config["cache_root"], app.config["keep_on_disk"], root
                )
        else:
            cache_file, cache_id = store_payload.find_file_from_headers(
                app.config["cache_root"], headers
            )

        root_dir_name = unpack_payload.extract_root_dir_name(cache_file)
        yield from verify_payload.verify_root(root_dir_name, headers)

        deploy_state.store(
            root_dir_name,
            cache_file,
            cache_id,
            app.config["deploy_root"],
            app.config["shared_lock"],
        )

        if unpack_data:
            yield from unpack_payload.unpack(cache_file, app.config["deploy_root"])

        result = {"root": root, "result": "Success", "result_code": 0}
    except exceptions.Fail as err:
        result = {"root": root, "result": str(err), "result_code": 1}
    except Exception as err:
        logger.exception(err)
        result = {"root": root, "result": "Fail", "result_code": 1}
    finally:
        yield result
