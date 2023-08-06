import copy
import datetime
import logging
import os
from typing import Callable, Dict, Optional

from flask import Flask
from flask import jsonify
from flask import redirect
from flask import request
from flask import send_from_directory
from flask_cors import CORS
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager
from flask_jwt_extended import verify_jwt_in_request
import sentry_sdk
from werkzeug.routing import IntegerConverter
from werkzeug.utils import safe_join

from katatachi.content import ContentStore
from katatachi.contrib.mod_view.update_one_button import UpdateOneButton
from katatachi.interface.api import ApiHandler
from katatachi.interface.mod_view.column_render import ButtonAfterCallbackBehavior
from katatachi.job import JobFactory
from katatachi.job import JobRunsStore
from katatachi.job import JobScheduler
from katatachi.mod_view import ModViewQuery
from katatachi.mod_view import ModViewRenderer
from katatachi.mod_view import ModViewStore
from katatachi.mod_view import NamedModViewColumn
from katatachi.pipeline import Pipeline
from katatachi.pipeline import PipelineModViewToState
from katatachi.pipeline import StateKey
from katatachi.reconciler import Reconciler
from katatachi.utils import DatabaseMigration
from katatachi.utils import getenv_or_raise
from katatachi.utils import WorkerPayload
from katatachi.utils import WorkerQueue
from katatachi.worker import GlobalMetadataStore
from katatachi.worker import MetadataStoreFactory
from katatachi.worker import WorkContextFactory
from katatachi.worker import WorkerCache
from katatachi.worker import WorkerConfigStore
from katatachi.worker import WorkerMetadata
from katatachi.worker import WorkFactory


class Application(object):
    # pipelines are instantiated with application so that
    # state migrations can be checked and run with database migration
    def __init__(self, pipeline: Optional[Pipeline] = None):
        # Environment variables
        if "SENTRY_DSN" in os.environ:
            print("SENTRY_DSN environ found, settings up sentry")
            sentry_sdk.init(os.environ["SENTRY_DSN"])
            sentry_enabled = True
        else:
            print("Not setting up sentry")
            sentry_enabled = False

        if os.environ.get("PAUSE_WORKERS", "false") == "true":
            self.pause_workers = True
        else:
            self.pause_workers = False

        self.instance_title = os.environ.get("INSTANCE_TITLE", "Untitled")

        # Database migration
        self.database_migration = DatabaseMigration(
            admin_connection_string=getenv_or_raise("MONGODB_ADMIN_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB"),
        )

        # Work factory
        self.content_store = ContentStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB"),
        )
        metadata_store_factory = MetadataStoreFactory(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB"),
        )
        self.worker_context_factory = WorkContextFactory(
            self.content_store, metadata_store_factory
        )
        self.worker_cache = WorkerCache()
        self.worker_config_store = WorkerConfigStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB"),
            worker_cache=self.worker_cache,
        )
        self.work_factory = WorkFactory(
            work_context_factory=self.worker_context_factory,
            worker_cache=self.worker_cache,
            worker_config_store=self.worker_config_store,
            sentry_enabled=sentry_enabled,
        )

        # Objects
        self.default_api_handler = None  # type: Optional[ApiHandler]
        self.mod_view_store = ModViewStore()
        self.boards_renderer = ModViewRenderer(self.content_store)
        self.job_runs_store = JobRunsStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB"),
        )
        self.worker_queue = WorkerQueue(
            redis_url=getenv_or_raise("REDIS_URL"),
            key_prefix=getenv_or_raise("REDIS_KEY_PREFIX"),
        )
        self.job_scheduler = JobScheduler(self.worker_queue)
        self.job_factory = JobFactory(
            self.job_scheduler, self.content_store, self.job_runs_store
        )

        self.pipeline = pipeline  # type: Optional[Pipeline]

        self.flask_app = None  # type: Optional[Flask]

    def register_worker_module(self, module_name: str, constructor: Callable):
        self.worker_cache.register_module(module_name, constructor)

    def register_job_module(self, module_name: str, constructor: Callable):
        self.job_scheduler.register_job_module(module_name, constructor)

    def set_default_api_handler(self, constructor: Callable):
        self.default_api_handler = constructor()

    def add_mod_view(self, name: str, mod_view: ModViewQuery):
        self.mod_view_store.add_mod_view(name, mod_view)

    def _configure_pipeline_workers(self):
        print("Configuring pipeline workers")
        if not self.pipeline:
            return

        # DO NOT CHANGE pipeline namespace, otherwise reconciliation won't find existing workers
        pipeline_namespace = f"pipeline.{self.pipeline.name}"
        actual_workers = self.worker_config_store.get_all(namespace=pipeline_namespace)
        desired_worker_ids = set()

        for pipeline_worker in self.pipeline.workers:
            worker_id = f"{pipeline_namespace}.{pipeline_worker.name}"

            # Register pipeline worker
            self.worker_cache.register_pipeline_worker(
                worker_id=worker_id, func=pipeline_worker.process
            )

            args = {
                "pipeline_name": self.pipeline.name,
                "from_state": pipeline_worker.from_state,
                "to_states": list(pipeline_worker.to_states),
                "limit": pipeline_worker.limit,
                "sort": pipeline_worker.sort,
            }

            desired_worker_ids.add(worker_id)
            if worker_id not in actual_workers:
                print(f"Adding pipeline worker {worker_id}")
                self.worker_config_store.add(
                    WorkerMetadata(
                        module_name=worker_id,
                        args=args,
                        interval_seconds=60,
                        error_resiliency=-1,
                    )
                )
            else:
                print(f"Updating pipeline worker {worker_id}")
                self.worker_config_store.update_args(worker_id, args)

        for worker_id in actual_workers.keys() - desired_worker_ids:
            print(f"Removing pipeline worker {worker_id}")
            self.worker_config_store.remove(worker_id)

        # Remove workers if the pipeline is renamed or removed
        # DO NOT CHANGE this namespace, otherwise reconciliation won't find existing workers
        actual_all_pipeline_workers = self.worker_config_store.get_all(
            namespace="pipeline"
        )
        for worker_id in actual_all_pipeline_workers.keys() - desired_worker_ids:
            print(f"Removing pipeline worker {worker_id} ({self.pipeline.name} gone)")
            self.worker_config_store.remove(worker_id)

    def _configure_pipeline_mod_views(self):
        print("Configuring pipeline mod views")
        if not self.pipeline:
            return

        def generate_mod_view_projections(
            to_state: PipelineModViewToState,
        ) -> NamedModViewColumn:
            update_set_doc = to_state.update_set_doc if to_state.update_set_doc else {}
            new_update_set_doc = copy.deepcopy(update_set_doc)
            new_update_set_doc[StateKey] = to_state.to_state

            return NamedModViewColumn(
                name=to_state.name,
                column=UpdateOneButton(
                    text=to_state.name,
                    filter_q_key=mod_view.filter_q_key,
                    update_set_doc=new_update_set_doc,
                    after_callback=ButtonAfterCallbackBehavior.RemoveRow,
                ),
            )

        # Add mod views
        for mod_view in self.pipeline.mod_views:
            self.add_mod_view(
                name=mod_view.name,
                mod_view=ModViewQuery(
                    query={StateKey: mod_view.from_state},
                    projections=mod_view.projections
                    + list(map(generate_mod_view_projections, mod_view.to_states)),
                    sort=mod_view.sort,
                ),
            )

    def get_flask_app(self) -> Flask:
        if self.flask_app:
            return self.flask_app

        # Configure Flask
        flask_app = Flask(__name__)
        CORS(flask_app)

        print("Initialing web app")
        self.database_migration.assert_latest()
        self._configure_pipeline_mod_views()
        self._configure_pipeline_workers()

        # Other objects
        global_metadata_store = GlobalMetadataStore(
            connection_string=getenv_or_raise("MONGODB_CONNECTION_STRING"),
            db=getenv_or_raise("MONGODB_DB"),
        )

        # Figure out path for static web artifact
        my_path = os.path.abspath(__file__)
        my_par_path = os.path.dirname(my_path)
        web_root = os.path.join(my_par_path, "web")
        if not os.path.exists(web_root):
            raise RuntimeError(f"Static web artifact is not found under {web_root}")

        # copy-pasta from https://github.com/pallets/flask/issues/2643
        class SignedIntConverter(IntegerConverter):
            regex = r"-?\d+"

        flask_app.url_map.converters["signed_int"] = SignedIntConverter

        # Less verbose logging from Flask
        werkzeug_logger = logging.getLogger("werkzeug")
        werkzeug_logger.setLevel(logging.ERROR)

        # Configure Flask JWT
        flask_app.config["JWT_SECRET_KEY"] = getenv_or_raise("JWT_SECRET_KEY")
        JWTManager(flask_app)
        admin_username = getenv_or_raise("ADMIN_USERNAME")
        admin_password = getenv_or_raise("ADMIN_PASSWORD")

        # Configure Flask paths and handlers
        def _before_request():
            r_path = request.path
            if r_path.startswith("/apiInternal"):
                verify_jwt_in_request()

        flask_app.before_request(_before_request)

        @flask_app.route("/auth", methods=["POST"])
        def _auth():
            username = request.json.get("username", None)
            password = request.json.get("password", None)
            if not username:
                return jsonify({"status": "error", "message": "Missing username"}), 400
            if not password:
                return jsonify({"status": "error", "message": "Missing password"}), 400
            if username != admin_username or password != admin_password:
                return (
                    jsonify({"status": "error", "message": "Wrong username/password"}),
                    401,
                )
            access_token = create_access_token(
                identity=username,
                expires_delta=datetime.timedelta(days=365),  # todo: just for now
            )
            return jsonify({"status": "ok", "access_token": access_token}), 200

        @flask_app.route("/", methods=["GET"])
        def _index():
            return redirect("/web")

        @flask_app.route("/health", methods=["GET"])
        def _health():
            return "OK", 200

        @flask_app.route("/api", methods=["GET"])
        @flask_app.route("/api/<path:path>", methods=["GET"])
        def _api(path=""):
            if not self.default_api_handler:
                return {"error": "no api"}, 404
            default_api_handler = self.default_api_handler  # type: ApiHandler
            result = default_api_handler.handle_request(
                path, request.args.to_dict(), self.content_store
            )
            return jsonify(result), 200

        @flask_app.route("/apiInternal/worker/modules", methods=["GET"])
        def _get_worker_modules():
            return (
                jsonify(
                    list(map(lambda m: m.to_json(), self.worker_cache.get_modules()))
                ),
                200,
            )

        @flask_app.route("/apiInternal/worker", methods=["POST"])
        def _add_worker():
            payload = request.json
            status, message_or_worker_id = self.worker_config_store.add(
                WorkerMetadata(
                    module_name=payload["module_name"],
                    args=payload["args"],
                    interval_seconds=payload["interval_seconds"],
                    error_resiliency=-1,
                )
            )
            if not status:
                return (
                    jsonify({"status": "error", "message": message_or_worker_id}),
                    400,
                )
            else:
                return jsonify({"status": "ok", "worker_id": message_or_worker_id}), 200

        @flask_app.route("/apiInternal/worker", methods=["GET"])
        def _get_workers():
            workers = []
            for worker_id, worker in self.worker_config_store.get_all().items():
                workers.append(
                    {
                        "worker_id": worker_id,
                        "module_name": worker.module_name,
                        "args": worker.args,
                        "interval_seconds": worker.interval_seconds,
                        "error_resiliency": worker.error_resiliency,
                        "last_executed_seconds": self.worker_config_store.get_last_executed_seconds(
                            worker_id
                        ),
                    }
                )
            return jsonify(workers), 200

        @flask_app.route("/apiInternal/worker/<string:worker_id>", methods=["DELETE"])
        def _remove_worker(worker_id: str):
            status, message = self.worker_config_store.remove(worker_id)
            if not status:
                return jsonify({"status": "error", "message": message}), 400
            else:
                return jsonify({"status": "ok"}), 200

        @flask_app.route(
            "/apiInternal/worker/<string:worker_id>/intervalSeconds/<int:interval_seconds>",
            methods=["PUT"],
        )
        def _update_worker_interval_seconds(worker_id: str, interval_seconds: int):
            status, message = self.worker_config_store.update_interval_seconds(
                worker_id, interval_seconds
            )
            if not status:
                return jsonify({"status": "error", "message": message}), 400
            else:
                return jsonify({"status": "ok"}), 200

        @flask_app.route(
            "/apiInternal/worker/<string:worker_id>/errorResiliency/<signed_int:error_resiliency>",
            methods=["PUT"],
        )
        def _update_worker_error_resiliency(worker_id: str, error_resiliency: int):
            status, message = self.worker_config_store.update_error_resiliency(
                worker_id, error_resiliency
            )
            if not status:
                return jsonify({"status": "error", "message": message}), 400
            else:
                return jsonify({"status": "ok"}), 200

        @flask_app.route(
            "/apiInternal/worker/<string:worker_id>/metadata", methods=["GET"]
        )
        def _get_worker_metadata(worker_id: str):
            return jsonify(global_metadata_store.get_all(worker_id)), 200

        @flask_app.route(
            "/apiInternal/worker/<string:worker_id>/metadata", methods=["POST"]
        )
        def _set_worker_metadata(worker_id: str):
            parsed_body = request.json
            global_metadata_store.set_all(worker_id, parsed_body)
            return jsonify({"status": "ok"}), 200

        @flask_app.route("/apiInternal/worker/<string:worker_id>/args", methods=["GET"])
        def _get_worker_args(worker_id: str):
            return jsonify(self.worker_config_store.get_args(worker_id)), 200

        @flask_app.route("/apiInternal/oneOffJob/modules", methods=["GET"])
        def _get_one_off_job_modules():
            return jsonify(self.job_scheduler.get_job_modules()), 200

        @flask_app.route("/apiInternal/oneOffJob/run", methods=["POST"])
        def _run_one_off_job():
            r = request.json
            self.job_scheduler.schedule_job(
                module_name=r["module_name"], args=r["args"]
            )
            return jsonify({"status": "ok"}), 200

        @flask_app.route("/apiInternal/oneOffJob/run", methods=["GET"])
        def _get_one_off_job_runs():
            return (
                jsonify(
                    list(
                        map(
                            lambda r: r.to_json(),
                            self.job_runs_store.get_job_runs_desc(),
                        )
                    )
                ),
                200,
            )

        @flask_app.route("/apiInternal/boards", methods=["GET"])
        def _get_boards():
            boards = []
            for (board_id, board_query) in self.mod_view_store.get_all():
                boards.append(
                    {
                        "board_id": board_id,
                        "board_query": board_query.to_dict(),
                        "count": self.content_store.count(board_query.query),
                    }
                )
            return jsonify(boards), 200

        def __render_board(board_id: str):
            board_query = self.mod_view_store.get(board_id)
            return (
                jsonify(
                    {
                        "board_query": board_query.to_dict(),
                        "payload": self.boards_renderer.render_as_dict(board_query),
                        "count": self.content_store.count(board_query.query),
                    }
                ),
                200,
            )

        @flask_app.route("/apiInternal/renderBoard/<string:board_id>", methods=["GET"])
        def _render_board(board_id: str):
            return __render_board(board_id)

        @flask_app.route(
            "/apiInternal/callbackBoard/<string:board_id>/<string:callback_id>",
            methods=["POST"],
        )
        def _callback_board(board_id: str, callback_id: str):
            document = request.json  # type: Dict
            self.boards_renderer.callback(callback_id, document)
            return __render_board(board_id)

        @flask_app.route("/apiInternal/pipeline", methods=["GET"])
        def _get_pipeline():
            if not self.pipeline:
                return None, 404

            source_workers = []
            for worker_id, worker in self.worker_config_store.get_all().items():
                if self.worker_cache.is_module_pipeline_source(worker.module_name):
                    source_workers.append(worker_id)

            return (
                jsonify(
                    {
                        "pipeline": self.pipeline.to_dict(self.content_store),
                        "sources": source_workers,
                    }
                ),
                200,
            )

        def _send_index() -> str:
            filename = safe_join(web_root, "index.html")
            with open(filename, "rb") as f:
                return (
                    f.read()
                    .decode("utf-8")
                    .replace("${INSTANCE_TITLE}", self.instance_title)
                )

        @flask_app.route("/web", methods=["GET"])
        @flask_app.route("/web/<path:filename>", methods=["GET"])
        def _web(filename=""):
            if filename == "":
                return _send_index()
            elif os.path.exists(os.path.join(web_root, *filename.split("/"))):
                return send_from_directory(web_root, filename)
            else:
                return _send_index()

        self.flask_app = flask_app
        return flask_app

    def start_web_dev(self):
        self.get_flask_app().run(
            host="0.0.0.0",
            port=int(os.getenv("PORT", 5000)),
            debug=True,
            # avoid using reloader for now
            # because there is no non-hacky way to tell if the app is running under gunicorn for production
            # and hence we should not add any conditional, including WERKZEUG_RUN_MAIN which is used for telling reload
            use_reloader=False,
        )

    def start_clock(self):
        self.database_migration.assert_latest()
        self._configure_pipeline_workers()
        reconciler = Reconciler(
            self.worker_config_store, self.worker_queue, self.pause_workers
        )
        try:
            reconciler.start()
        except (KeyboardInterrupt, SystemExit):
            print("Reconciler stopping...")
            reconciler.stop()

    def start_worker(self):
        self.database_migration.assert_latest()
        self._configure_pipeline_workers()
        try:
            while True:
                payload = self.worker_queue.blocking_dequeue()
                if payload.type == "worker":
                    self._run_worker(payload)
                elif payload.type == "job":
                    self._run_job(payload)

        except (KeyboardInterrupt, SystemExit):
            print("Worker stopping...")

    def start_database_migration(self):
        print("---------")
        self.database_migration.migrate()
        if self.pipeline:
            print("---------")
            self.pipeline.assert_valid_state_migrations(self.content_store)
            print("---------")
            self.pipeline.perform_state_migrations(self.content_store)

    def _run_worker(self, payload: WorkerPayload):
        module_name, args = payload.module_name, payload.args
        work_func_and_id = self.work_factory.get_work_func(module_name, args)
        if not work_func_and_id:
            return
        work_func, worker_id = work_func_and_id
        work_func()

    def _run_job(self, payload: WorkerPayload):
        module_name, args = payload.module_name, payload.args
        job_func_and_id = self.job_factory.get_job_func(module_name, args)
        if not job_func_and_id:
            return
        job_func, job_id = job_func_and_id
        job_func()
