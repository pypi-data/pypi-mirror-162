import queue
import config
import requests
import os
from callback_defs import CallbackArgs, Prompt, Result


def post(self, result: Result, prompt: Prompt) -> None:
    "upload to s3, then to signal bot imogen"
    bearer = "Bearer " + config.get_secret("SUPABASE_API_KEY")
    mime = "video/mp4" if result.filepath.endswith("mp4") else "image/png"
    # TODO: supabase url as envvar
    # iterate over filepaths if applicable
    requests.post(
        f"https://fqbyocakhbhchhfvnkcu.supabase.co/storage/v1/object/imoges/{prompt.slug}.png",
        headers={"Authorization": bearer, "Content-Type": mime},
        data=open(result.filepath, mode="rb").read(),
    )
    minutes, seconds = divmod(result.elapsed, 60)
    f = open(result.filepath, mode="rb")
    message = f"{prompt.prompt}\nTook {minutes}m{seconds}s to generate,"
    if result.loss and result.loss != -1:
        message += f"{result.loss} loss,"
    # message += f" v{clipart.version}."
    for i in range(3):
        try:
            resp = requests.post(
                f"{prompt.webhook or admin_signal_url}/attachment",
                params={"message": message, "id": str(prompt.prompt_id)},
                files={"image": f},
            )
            logging.info(resp)
            break
        except requests.RequestException:
            logging.info("pausing before retry")
            time.sleep(i)
    os.remove(result.filepath)


def signal_webhook(q: queue.Queue, output_queue: queue.Queue):
    pass
