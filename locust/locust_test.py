import random
from functools import cache
from pathlib import Path

from locust import HttpUser, between, task

path_mapping = {
    "chat": Path("./locust/data/chat_post.json"),
    "completion_parameter": Path("./locust/data/completion_parameters_post.json"),
    "message": Path("./locust/data/message_post.json"),
    "prompt": Path("./locust/data/prompt_post.json"),
    "prompt_template": Path("./locust/data/prompt_template_post.json"),
}


@cache
def get_payload(path: Path) -> str:
    with open(path) as file:
        return file.read()


class ApiUser(HttpUser):
    id_set = set()
    index_set = {0}
    wait_time = between(1, 5)
    sorting_fields = ["updated_at", "created_at", "id"]

    @task
    def get_chat(self):
        chat_id = self.get_id()
        if not chat_id:
            return
        self.client.get(
            f"/v1/chat/{chat_id}",
            name="/v1/chat/{id}",
        )

    @task
    def post_chat(self):
        response = self.client.post(
            "/v1/chat",
            data=get_payload(
                path_mapping.get("chat"),
            ),
            name="/v1/chat",
        )
        if response.status_code == 201:
            self.id_set.add(response.json().get("id"))

    @task
    def patch_chat_message(self):
        chat_id = self.get_id()
        if not chat_id:
            return
        self.client.patch(
            f"/v1/chat/{chat_id}/messages/{self.get_index()}",
            data=get_payload(path_mapping.get("message")),
            name="/v1/chat/{id}/messages/{index}",
        )

    @task
    def delete_chat(self):
        chat_id = self.get_id()
        if not chat_id:
            return
        response = self.client.delete(
            f"/v1/chat/{chat_id}",
            name="/v1/chat/{id}",
        )
        if response.status_code == 204:
            self.id_set.remove(chat_id)

    @task
    def put_chat(self):
        chat_id = self.get_id()
        if not chat_id:
            return
        self.client.put(
            f"/v1/chat/{chat_id}",
            data=get_payload(
                path_mapping.get("chat"),
            ),
            name="/v1/chat/{id}",
        )

    @task
    def search_chat(self):
        self.client.get(
            "/v1/chat",
            params={
                "offset": random.randint(1, 20),
                "limit": random.randint(1, 20),
                "sorting_field": random.sample(self.sorting_fields, 1),
                "ascending": random.sample([False, True], 1),
            },
            name="/v1/chat",
        )

    def get_id(self) -> int:
        try:
            return random.sample(list(self.id_set), k=1)[0]
        except ValueError:
            return None

    def get_index(self) -> int:
        return random.sample(list(self.index_set), k=1)[0]
