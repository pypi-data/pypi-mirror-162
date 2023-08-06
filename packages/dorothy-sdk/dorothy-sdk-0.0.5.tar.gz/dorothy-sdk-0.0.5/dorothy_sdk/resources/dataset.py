from typing import List
from dorothy_sdk.session import Session
from dorothy_sdk.utils import url_join
from dorothy_sdk.resources.image import Image


class Dataset:
    resource = "datasets"

    def __init__(self, name: str, image_formats: str, number_images: int, session: Session, host: str, *args, **kwargs):
        self.number_images = number_images
        self.name = name
        self.image_formats = image_formats
        self._session = session
        self._service_host = host

    def list_images(self) -> List[Image]:
        request = self._session.get(url_join(self._service_host, Image.resource), params={"search": self.name})
        request.raise_for_status()
        if request.status_code == 200:
            return [Image(session=self._session, host=self._service_host, **element) for element in request.json()]
        else:
            raise RuntimeError("Unable to list available images")

    def get_image(self, image_id: str) -> Image:
        request = self._session.get(url_join(self._service_host, Image.resource), params={"search": f"{self.name},{image_id}"})
        if request.status_code == 200:
            return Image(session=self._session, host=self._service_host, **request.json())
        elif request.status_code == 404:
            return None
        else:
            raise RuntimeError("Unable to fetch image")
