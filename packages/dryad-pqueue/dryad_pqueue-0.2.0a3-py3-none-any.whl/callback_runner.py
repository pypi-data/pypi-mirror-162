import time
import sys
import pickle
import callback_defs
import threading
import psycopg
import json
import queue
import callback_handlers

# this is kinda icky
class subpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "pqueue.callback_defs":
            return getattr(callback_defs, name)
        return super().find_class(module, name)


print("Just started callback_runner.py")

callback_handlers = {
    "upload_images": callback_handlers.upload_images_supabase,
    "upload_images_webp": callback_handlers.upload_images_webp_supabase,
    "combined_image": callback_handlers.combine_and_upload_image,
}

conn = None

callback_threads = {}
output_queue = queue.Queue()
for callback_type, handler in callback_handlers.items():
    q = queue.Queue()
    thread = threading.Thread(
        target=handler, name=callback_type, args=(q, output_queue)
    )
    thread.start()
    callback_threads[callback_type] = q

while 1:
    results: callback_defs.CallbackArgs = subpickler(sys.stdin.buffer).load()

    if conn == None:
        conn = psycopg.connect(results.database_url, autocommit=True)

    # Every callback outputs a dict. We merge these dicts together and upload
    # them as they come back.
    data_dictionary = {}
    for callback in results.prompt.callbacks:
        callback_queue: queue.Queue = callback_threads[callback["type"]]
        callback_queue.put(
            {
                "images": results.result.images,
                "prompt": results.prompt,
                "supabase_key": results.supabase_key,
                **callback,
            }
        )

    conn.execute(
        """UPDATE prompt_queue_new SET status='uploading', generation_info=%s::jsonb WHERE id=%s;""",
        [json.dumps(results.generation_metadata), results.prompt.prompt_id],
    )

    last_data_dictionary = json.dumps(data_dictionary)

    set_done = False
    for i in range(len(results.prompt.callbacks)):
        try:
            result = output_queue.get(timeout=30)
        except queue.Empty:
            print("timeout error")
            continue
        if not result:
            continue

        data_dictionary.update(result)
        status = "done" if "image_urls" in data_dictionary else "uploading"
        set_done = status == "done"
        last_data_dictionary = json.dumps(data_dictionary)
        print("writing", last_data_dictionary)
        conn.execute(
            f"""UPDATE prompt_queue_new SET status='{status}', outputs=%s::jsonb WHERE id=%s;""",
            [
                last_data_dictionary,
                results.prompt.prompt_id,
            ],
        )

    print(f"Finished at {time.time()-results.start_time:.2f}")
    # TODO: "postprocessed?"
    if not set_done:
        conn.execute(
            """UPDATE prompt_queue_new SET status='done' WHERE id=%s;""",
            [results.prompt.prompt_id],
        )
