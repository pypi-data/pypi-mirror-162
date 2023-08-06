import grpc

from .proto import (
    ref_pb2, ref_pb2_grpc,
    commit_pb2, commit_pb2_grpc,
    blob_pb2_grpc,
    )
from .proto import shared_pb2
from ..errors import GitlabArtifactsError

GITALY_ADDR = 'unix:/var/opt/gitlab/gitaly/gitaly.socket'
REF_PREFIX = 'refs/heads/'

def _gitaly_repo(project):
    return shared_pb2.Repository(
        storage_name=project.storage,
        relative_path=project.disk_path,
        gl_repository=project.gl_repository,
        )


class GitalyClient():
    def __init__(self, addr=GITALY_ADDR):
        self.addr = addr
        self._channel = None
        self._refsvc = None
        self._commitsvc = None
        self._blobsvc = None

    def __enter__(self):
        self._channel = grpc.insecure_channel(self.addr)
        self._refsvc = ref_pb2_grpc.RefServiceStub(self._channel)
        self._commitsvc = commit_pb2_grpc.CommitServiceStub(self._channel)
        self._blobsvc = blob_pb2_grpc.BlobServiceStub(self._channel)

        return self

    def __exit__(self, *args):
        self._channel.close()

    @staticmethod
    def name_from_ref(ref):
        if ref.lower().startswith(REF_PREFIX):
            return ref[len(REF_PREFIX):]
        return ref

    def get_branches(self, project):
        repository = _gitaly_repo(project)
        request = ref_pb2.FindAllBranchesRequest(
            repository=repository
            )

        branches = []
        try:
            # Gitaly "chunks?" responses at 20 items
            for page in self._refsvc.FindAllBranches(request):
                for branch in page.branches:
                    ref = (
                        GitalyClient.name_from_ref(branch.name.decode('utf-8')),
                        branch.target.id,
                        )
                    branches.append(ref)
        except grpc.RpcError as e:
            raise GitlabArtifactsError(
                'RefSvc.FindAllBranches for {} failed with error {}:{}'.format(
                    project.full_path,
                    e.code(),
                    e.details()
                    )
                ) from e

        # Safety check for failed requests
        if not branches:
            raise GitlabArtifactsError(
                'Gitaly returned no branches for {}'.format(
                    project.full_path
                    )
                )

        return branches

    def get_tags(self, project):
        repository = _gitaly_repo(project)
        request = ref_pb2.FindAllTagsRequest(
            repository=repository
            )

        tags = []
        try:
            # Gitaly "chunks?" responses at 20 items
            for page in self._refsvc.FindAllTags(request):
                for tag in page.tags:
                    ref = (
                        GitalyClient.name_from_ref(tag.name.decode('utf-8')),
                        tag.target_commit.id,
                        )
                    tags.append(ref)
        except grpc.RpcError as e:
            raise GitlabArtifactsError(
                'RefSvc.FindAllTags for {} failed with error {}:{}'.format(
                    project.full_path,
                    e.code(),
                    e.details()
                    )
                ) from e

        return tags

    def get_tree_entry(self, ref, path):
        repository = _gitaly_repo(ref.project)
        request = commit_pb2.TreeEntryRequest(
            repository=repository,
            revision=ref.commit.encode('utf-8'),
            path=path.encode('utf-8'),
            limit=0,
            )

        try:
            # If the file does not exist, this raises RpcError.code = StatusCode.NOT_FOUND
            response = list(self._commitsvc.TreeEntry(request))
        except grpc.RpcError as e:
            # Return a nil file if the entry was not found
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return (None,)*3

            raise GitlabArtifactsError(
                'CommitSvc.TreeEntry failed with error {}:{}'.format(
                    e.code(),
                    e.details()
                    )
                ) from e

        # We should always get a response - it may be empty
        if not response:
            raise GitlabArtifactsError(
                'CommitSvc.TreeEntry did not return a response')

        first_entry = response[0]

        # Return a nil file if the first entry is not type=BLOB
        # Old versions of GitLab (<14) return type=COMMIT for non-existent files
        if first_entry.type != 1:
            return (None,)*3

        return (
            first_entry.oid,
            first_entry.size,
            b''.join(entry.data for entry in response)
            )
