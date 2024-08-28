import os
from huggingface_hub import HfApi
from genki_dama.model.creative_model import CreativeModel
from model.storage.disk import utils
from constants import CompetitionParameters, MAX_HUGGING_FACE_BYTES

from model.storage.remote_model_store import RemoteModelStore
from huggingface_hub import HfApi, file_exists
from collections import defaultdict


def shared_pointers(tensors):
    ptrs = defaultdict(list)
    for k, v in tensors.items():
        ptrs[v.data_ptr()].append(k)
    failing = []
    for ptr, names in ptrs.items():
        if len(names) > 1:
            failing.append(names)
    return failing
 

class HuggingFaceModelStore(RemoteModelStore):
    """Hugging Face based implementation for storing and retrieving a model."""

    @classmethod
    def assert_access_token_exists(cls) -> str:
        """Asserts that the access token exists."""
        if not os.getenv("HF_ACCESS_TOKEN"):
            raise ValueError("No Hugging Face access token found to write to the hub.")
        return os.getenv("HF_ACCESS_TOKEN")

    async def upload_model(
        self,
        model: CreativeModel,
        local_repo_dir: str,
    ) -> CreativeModel:
        """Uploads a trained model to Hugging Face."""
        token = HuggingFaceModelStore.assert_access_token_exists()
        api = HfApi(token=token)
        api.create_repo(
            repo_id=model.namespace + "/" + model.name,
            exist_ok=True,
            private=True,
        )

        # upload model.local_repo_dir to Hugging Face
        commit_info = api.upload_folder(
            repo_id=model.namespace + "/" + model.name,
            folder_path=local_repo_dir,
            commit_message="Upload model",
            repo_type="model",
        )

        creative_model_with_commit = CreativeModel(
            namespace=model.namespace,
            name=model.name,
            hash=model.hash,
            commit=commit_info.oid,
            competition_id=model.competition_id,
        )

        return creative_model_with_commit
        # # TODO consider skipping the redownload if a hash is already provided.
        # # To get the hash we need to redownload it at a local tmp directory after which it can be deleted.
        # with tempfile.TemporaryDirectory() as temp_dir:
        #     model_with_hash = await self.download_model(
        #         model_id_with_commit, temp_dir, competition_parameters
        #     )
        #     # Return a ModelId with both the correct commit and hash.
        #     return model_with_hash.id

    async def download_model(
        self,
        creative_model: CreativeModel,
        local_path: str,
        model_parameters: CompetitionParameters,
    ) -> CreativeModel:
        """Retrieves a trained model from Hugging Face."""
        if not creative_model.commit:
            raise ValueError("No Hugging Face commit id found to read from the hub.")

        repo_id = creative_model.namespace + "/" + creative_model.name

        # Check ModelInfo for the size of model.safetensors file before downloading.
        try:
            token = HuggingFaceModelStore.assert_access_token_exists()
        except:
            token = None
        api = HfApi(token=token)
        model_info = api.model_info(repo_id=repo_id, revision=creative_model.commit, timeout=10, files_metadata=True)
        size = sum(repo_file.size for repo_file in model_info.siblings)
        if size > MAX_HUGGING_FACE_BYTES:
            raise ValueError(f"Hugging Face repo over maximum size limit. Size {size}. Limit {MAX_HUGGING_FACE_BYTES}.")

        api.hf_hub_download(
            repo_id=repo_id,
            revision=creative_model.commit,
            filename="checkpoint.safetensors",
            cache_dir=local_path,
        )

        # Get the directory the model was stored to.
        model_dir = utils.get_hf_download_path(local_path, creative_model)

        # Realize all symlinks in that directory since Transformers library does not support avoiding symlinks.
        utils.realize_symlinks_in_directory(model_dir)

        # Compute the hash of the downloaded model.
        model_hash = utils.get_hash_of_directory(model_dir)
        creative_model_with_hash = CreativeModel(
            namespace=creative_model.namespace,
            name=creative_model.name,
            commit=creative_model.commit,
            hash=model_hash,
            competition_id=creative_model.competition_id,
        )

        return creative_model_with_hash
