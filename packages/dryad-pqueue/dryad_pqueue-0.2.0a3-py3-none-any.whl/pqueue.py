#!/usr/bin/python3.9
# Copyright (c) 2022 Sylvie Liberman
# pylint: disable=subprocess-run-check
import logging
import os
import pickle
import socket
import subprocess
import sys
import time
import traceback
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Optional
import psycopg
import requests
from psycopg.rows import class_row
import config
from callback_defs import CallbackArgs, Prompt, Result

hostname = socket.gethostname()
admin_signal_url = "https://imogen-dryad.fly.dev"


def admin(msg: str) -> None:
    """send a message to admin"""
    logging.info(msg)
    requests.post(
        f"{admin_signal_url}/admin",
        params={"message": str(msg)},
    )


Gen = Any  # Optional[clipart.Generator]


class Maestro:
    model: str
    version = "unknown"

    def stop(self) -> None:
        "check envvars if we should exit depending on where we're running, or sleep"
        paid = "" if os.getenv("FREE") else "paid "
        logging.debug("stopping")
        if os.getenv("POWEROFF"):
            admin(
                f"\N{cross mark}{paid}\N{frame with picture}\N{construction worker}\N{high voltage sign}\N{downwards black arrow} {hostname}"
            )
            subprocess.run(["sudo", "poweroff"])
        elif os.getenv("EXIT"):
            admin(
                f"\N{cross mark}{paid}\N{frame with picture}\N{construction worker}\N{sleeping symbol} {hostname}"
            )
            sys.exit(0)
        else:
            time.sleep(15)

    def maybe_scale_in(self, conn: psycopg.Connection) -> None:
        "check the ratio of paid prompts to paid workers and potentially stop"
        if not os.getenv("EXIT_ON_LOAD"):
            return
        workers = conn.execute(
            "select count(distinct hostname) + 1 from prompt_queue where status='assigned'"
        ).fetchone()[0]
        queue_empty = conn.execute(
            "SELECT count(id)=0 FROM prompt_queue WHERE status='pending'"
        ).fetchone()[0]
        paid_queue_size = conn.execute(
            "SELECT count(id) AS len FROM prompt_queue WHERE status='pending' OR status='assigned' AND paid=TRUE;"
        ).fetchone()[0]
        if queue_empty:
            admin(
                f"\N{scales}\N{chart with downwards trend}\N{octagonal sign} {hostname}"
            )
            sys.exit(0)
        if workers == 1:
            # nobody else has taken assignments, we just finished ours
            return
        if paid_queue_size / workers < 5 or workers > 6:
            # target metric: latency under 10 min for paid images
            # images take ~2min
            # if there's less than five items per worker, we aren't needed
            # even if there's 25 items, we still don't want more than five workers
            admin(
                f"paid queue size: {paid_queue_size}. workers: {workers}. load: {paid_queue_size / workers}. exiting {hostname}"
            )
            sys.exit(0)

    def get_prompt(self, conn: psycopg.Connection) -> Optional[Prompt]:
        "try to get a prompt and mark it as assigned if possible"
        # mark prompts that have been assigned for more than 10 minutes as unassigned
        conn.execute(
            """UPDATE prompt_queue SET status='pending', assigned_ts=null
            WHERE status='assigned' AND assigned_ts  < (now() - interval '5 minutes');"""
        )  # maybe this is a trigger
        # try to select something
        # TODO: batching
        maybe_id = conn.execute(
            """SELECT id FROM prompt_queue WHERE status='pending'
            AND model=%s ORDER BY priority DESC, id ASC LIMIT 1;""",
            [self.model],
        ).fetchone()
        if not maybe_id:
            return None
        prompt_id = maybe_id[0]
        cursor = conn.cursor(row_factory=class_row(Prompt))
        logging.info("getting")
        # mark it as assigned, returning only if it got updated
        maybe_prompt = cursor.execute(
            """UPDATE prompt_queue SET status='assigned', assigned_ts=now(), hostname=%s
            WHERE id = %s AND status='pending'
            RETURNING id AS prompt_id, callbacks, params, inserted_ts, num_images;""",
            [hostname, prompt_id],
        ).fetchone()
        if not maybe_prompt:
            logging.warning("couldn't actually get a prompt")
        logging.info("set assigned")
        return maybe_prompt

    def main(self) -> None:
        "setup, get prompts, handle them, mark as uploading, upload, mark done"
        Path("./input").mkdir(exist_ok=True)
        admin(f"\N{artist palette}\N{construction worker}\N{hiking boot} {hostname}")
        logging.info("starting postgres_jobs on %s", hostname)
        # clear failed instances
        # try to get an id. if we can't, there's no work, and we should stop
        # try to claim it. if we can't, someone else took it, and we should try again
        # generate the prompt
        backoff = 60.0
        generator = None
        supabase_key = config.get_secret("SUPABASE_API_KEY", fail_if_none=True)
        database_url = config.get_secret("DATABASE_URL", fail_if_none=True)
        conn = psycopg.connect(database_url, autocommit=True)
        callback_location = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "callback_runner.py"
        )
        callback_runner = subprocess.Popen(
            ["/usr/bin/python3.10", callback_location],
            stdin=subprocess.PIPE,
            close_fds=False,
        )
        # catch some database connection errors
        try:
            while 1:
                # try to claim
                t0 = time.time()
                prompt = self.get_prompt(conn)
                if not prompt:
                    self.stop()
                    continue
                logging.info("got prompt: %s", prompt)
                try:
                    generator, result = self.handle_item(generator, prompt)
                    # # success
                    # start_post = time.time()
                    # set_upload = """UPDATE prompt_queue SET status='uploading', elapsed_gpu=%s, url=%s, generation_info=%s::jsonb WHERE id=%s;"""
                    # params = [
                    #     result.elapsed,
                    #     f"https://fqbyocakhbhchhfvnkcu.supabase.co/storage/v1/object/public/imoges/{prompt.prompt_id}.png",
                    #     json.dumps({"seed": result.seed, "loss": result.loss}), # include version
                    #     prompt.prompt_id,
                    # ]
                    # logging.info("set uploading %s", prompt)
                    # conn.execute(set_upload, params)
                    # self.post(result, prompt)
                    # conn.execute(
                    #     "UPDATE prompt_queue SET status='done' WHERE id=%s",
                    #     [prompt.prompt_id],
                    # )
                    # logging.info(
                    #     "set done, poasting time: %s", time.time() - start_post
                    # )
                    backoff = 60
                except Exception as e:  # pylint: disable=broad-except
                    logging.info("caught exception")
                    error_message = traceback.format_exc()
                    if prompt:
                        admin(repr(prompt))
                    logging.error(error_message)
                    admin(error_message)
                    conn.execute(
                        "UPDATE prompt_queue SET status='pending', errors=errors+1 WHERE id=%s",
                        [prompt.prompt_id],
                    )
                    if "out of memory" in str(e).lower():
                        sys.exit(137)
                    time.sleep(backoff)
                    backoff *= 1.5

                print(f"Got result {time.time()-t0:.2f}")
                generation_metadata = {
                    "seed": result.seed,
                    "loss": result.loss,
                    "time_elapsed": result.elapsed,
                    "model_version": self.version,
                }
                callback_args = CallbackArgs(
                    result, prompt, supabase_key, database_url, generation_metadata, t0
                )
                print(f"About to start callback runner {time.time()-t0:.2f}")
                print(f"Started callback runner {time.time()-t0:.2f}")
                if True:  # development
                    pickle.dump(
                        callback_args, open("callback_args.pickle", "wb"), protocol=5
                    )

                try:
                    assert callback_runner.stdin
                    callback_runner.stdin.write(pickle.dumps(callback_args, protocol=5))
                except (BrokenPipeError, AssertionError):  # Process died
                    print("Callback runner died, restarting")
                    callback_runner = subprocess.Popen(
                        ["/usr/bin/python3.10", callback_location],
                        stdin=subprocess.PIPE,
                        close_fds=False,
                    )
                # print("callback results", callback_runner.communicate(pickle.dumps(callback_args, protocol=5)))
                # pickle.dump(callback_args, callback_runner.stdin)
                print(f"Serialized args {time.time()-t0:.2f}")

                self.maybe_scale_in(conn)
        finally:
            conn.close()

    # parse raw parameters
    # parse prompt list
    # it's either a specific function or the default one
    # for imagegen, if there's an initial image, download it from postgres or redis
    # pass maybe raw parameters and initial parameters to the function to get loss and a file
    # if it's a list of prompts, generate a video using the slug
    # make a message with the prompt, time, loss, and version
    # upload the file, id, and message to imogen based on the url. ideally retry on non-200
    # (imogen looks up destination, author, timestamp to send).
    # upload to twitter. if it fails, maybe log video size

    def create_generator(self) -> Gen:
        raise NotImplementedError("override this method")

    def handle_item(self, generator: Gen, prompt: Prompt) -> tuple[Gen, Result]:
        "finagle settings, generate it depending on settings, make a video if appropriate"
        # params can override inputs
        namespace = {
            "num_images": prompt.num_images,
            **prompt.params,
        }
        args = SimpleNamespace(**namespace)
        logging.info(args)
        start_time = time.time()
        if not generator:
            generator = self.create_generator()
        images = generator.generate(args)
        # return the generator so it can be reused
        return generator, Result(
            elapsed=round(time.time() - start_time),
            # filepaths? dir?
            images=images,
            loss=-1,
            seed="",
            version=self.version,
        )


if __name__ == "__main__":
    Maestro().main()
