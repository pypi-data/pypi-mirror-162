import requests
import io
import threading
import queue
from PIL import Image


def upload_webp_image(image_queue: queue.Queue, url_queue: queue.Queue):
    while 1:
        stuff = image_queue.get()
        prompt_id = stuff["prompt_id"]
        i = stuff["i"]
        bearer = stuff["bearer"]
        image = stuff["image"]

        buf = io.BytesIO()
        image.save(buf, format="webp")
        buf.seek(0)
        buffer = buf.read()
        r = requests.post(
            f"https://fqbyocakhbhchhfvnkcu.supabase.co/storage/v1/object/new-images-webp/{prompt_id}/{i}.webp",
            headers={"Authorization": bearer, "Content-Type": "image/webp"},
            data=buffer,
        )
        image_queue.task_done()
        if r.status_code != 200:
            print("Got status code", r.status_code, "and content", r.text)
        else:
            url_queue.put(
                f"https://fqbyocakhbhchhfvnkcu.supabase.co/storage/v1/object/public/new-images-webp/{prompt_id}/{i}.webp"
            )


def upload_images_webp_supabase(q: queue.Queue, output_queue: queue.Queue):
    image_queue = queue.Queue()
    url_queue = queue.Queue()
    threads: list[threading.Thread] = []
    for i in range(9):
        thread = threading.Thread(
            target=upload_webp_image, args=(image_queue, url_queue)
        )
        thread.start()
        threads.append(thread)

    while 1:
        value = q.get()
        bearer = "Bearer " + value["supabase_key"]
        prompt_id = value["prompt"].prompt_id
        for i, image in enumerate(value["images"]):
            image_queue.put(
                {"prompt_id": prompt_id, "i": i, "bearer": bearer, "image": image}
            )
        image_queue.join()

        urls = []
        while 1:
            try:
                urls.append(url_queue.get_nowait())
            except queue.Empty:
                break

        # only update if we succeeded
        if len(urls) == len(value["images"]):
            urls.sort()
            output_queue.put({"image_urls_webp": urls})
        else:
            output_queue.put({})
