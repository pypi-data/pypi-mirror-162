from . import image_combiner
import requests
import io
import queue


def combine_and_upload_image(q: queue.Queue, output_queue: queue.Queue):
    print("combine and upload image start")
    while 1:
        value = q.get()
        bearer = "Bearer " + value["supabase_key"]
        prompt_id = value["prompt"].prompt_id
        prompt_text = ", ".join(
            [prompt["text"] for prompt in value["prompt"].params["prompts"]]
        )
        image = image_combiner.make_image_simple(value["images"], prompt_text)

        buf = io.BytesIO()
        image.save(buf, format="webp")
        buf.seek(0)
        buffer = buf.read()

        r = requests.post(
            f"https://fqbyocakhbhchhfvnkcu.supabase.co/storage/v1/object/new-images/{prompt_id}/combined_image.webp",
            headers={"Authorization": bearer, "Content-Type": "image/webp"},
            data=buffer,
        )
        if r.status_code != 200:
            print("Got status code", r.status_code, "and content", r.text)
            output_queue.put({})
        else:
            output_queue.put(
                {
                    "combined_image": f"https://fqbyocakhbhchhfvnkcu.supabase.co/storage/v1/object/public/new-images/{prompt_id}/combined_image.webp"
                }
            )
