import io
import os
from typing import Dict, List

import numpy as np
from docarray import Document, DocumentArray
from now_common import options
from now_common.utils import setup_clip_music_apps
from PIL import Image

from now.apps.base.app import JinaNOWApp
from now.constants import (
    CLIP_USES,
    IMAGE_MODEL_QUALITY_MAP,
    Apps,
    Modalities,
    Qualities,
)
from now.now_dataclasses import UserInput


class TextToVideo(JinaNOWApp):
    def __init__(self):
        super().__init__()

    @property
    def app_name(self) -> str:
        return Apps.TEXT_TO_VIDEO

    @property
    def is_enabled(self) -> bool:
        return True

    @property
    def description(self) -> str:
        return 'Text to video search app'

    @property
    def input_modality(self) -> Modalities:
        return Modalities.TEXT

    @property
    def output_modality(self) -> Modalities:
        return Modalities.VIDEO

    @property
    def required_docker_memory_in_gb(self) -> int:
        return 12

    @property
    def options(self) -> List[Dict]:
        return [options.QUALITY_CLIP]

    def set_flow_yaml(self, **kwargs):
        finetuning = kwargs.get('finetuning', False)
        encode = kwargs.get('encode', False)
        if finetuning + encode > 1:
            raise ValueError(
                f"Can't set flow to more than one mode but have encode={encode}, finetuning={finetuning}"
            )

        flow_dir = os.path.abspath(os.path.join(__file__, '..'))

        if finetuning:
            self.flow_yaml = os.path.join(flow_dir, 'ft-flow-video-clip.yml')
        elif encode:
            self.flow_yaml = os.path.join(flow_dir, 'encode-flow-video-clip.yml')
        else:
            self.flow_yaml = os.path.join(flow_dir, 'flow-video-clip.yml')

    @property
    def pre_trained_embedding_size(self) -> Dict[Qualities, int]:
        return {
            Qualities.MEDIUM: 512,
            Qualities.GOOD: 512,
            Qualities.EXCELLENT: 768,
        }

    def setup(
        self, dataset: DocumentArray, user_input: UserInput, kubectl_path
    ) -> Dict:
        return setup_clip_music_apps(
            app_instance=self,
            user_input=user_input,
            dataset=dataset,
            encoder_uses=CLIP_USES,
            encoder_uses_with={
                'pretrained_model_name_or_path': IMAGE_MODEL_QUALITY_MAP[
                    user_input.quality
                ][1]
            },
            indexer_uses='DocarrayIndexerV2',
            finetune_datasets=(),
            kubectl_path=kubectl_path,
        )

    def load_from_folder(self, path: str) -> DocumentArray:
        return DocumentArray.from_files(path + '/**')

    def preprocess(self, da: DocumentArray, user_input: UserInput) -> DocumentArray:
        def convert_fn(d: Document):
            try:
                if d.blob == b'':
                    if d.uri:
                        d.load_uri_to_blob()
                    elif d.tensor is not None:
                        d.convert_tensor_to_blob()
                sample_video(d)
            except:
                pass
            return d

        def gen():
            def _get_chunk(batch):
                return [convert_fn(d) for d in batch]

            for batch in da.map_batch(
                _get_chunk, batch_size=4, backend='process', show_progress=True
            ):
                for d in batch:
                    yield d

        da = DocumentArray(d for d in gen())
        return DocumentArray(d for d in da if d.blob != b'')


def select_frames(num_selected_frames, num_total_frames):
    partition_size = num_total_frames / (num_selected_frames + 1)
    return [round(partition_size * (i + 1)) for i in range(num_selected_frames)]


def sample_video(d):
    video = d.blob
    video_io = io.BytesIO(video)
    gif = Image.open(video_io)
    frame_indices = select_frames(3, gif.n_frames)
    frames = []
    for i in frame_indices:
        gif.seek(i)
        frame = np.array(gif.convert("RGB"))
        frame_pil = Image.fromarray(frame)
        frame_pil_resized = frame_pil.resize((224, 224))
        frames.append(frame_pil_resized)
        frame_bytes = io.BytesIO()
        frame_pil_resized.save(frame_bytes, format="JPEG", quality=70)
        d.chunks.append(Document(blob=frame_bytes.getvalue()))
    small_gif_bytes_io = io.BytesIO()
    frames[0].save(
        small_gif_bytes_io,
        "gif",
        save_all=True,
        append_images=frames[1:],
        optimize=False,
        duration=300,
        loop=0,
        quality=75,
    )
    d.blob = small_gif_bytes_io.getvalue()
