import gzip
import shutil
from functools import reduce
from pathlib import Path

import requests
from tqdm import tqdm


def _p(pth):
    return Path(pth).expanduser()


class Source:
    priority = 100

    def ensure(self, dest):
        dest.parent.mkdir(parents=True, exist_ok=True)

    def get_path(self, dest):
        raise NotImplementedError()

    def __call__(self, dest):
        path = self.get_path(dest)
        if path.exists():
            return path
        else:
            return self.acquire(dest)


class LocalSource(Source):
    priority = 1000

    def __init__(self, path):
        self.path = _p(path)

    def get_path(self, dest):
        return self.path

    def acquire(self, dest):
        return False
        # return self.path.exists() and self.path


class HttpSource(Source):
    def __init__(self, url):
        self.url = url
        self.filename = url.split("/")[-1]

    @staticmethod
    def download(url, filename):
        """Download the given url into the given filename."""
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            print(f"Skip {url} ({r.status_code})")
            return False
        print(f"Downloading {url}")
        total = int(r.headers.get("content-length") or "1024")
        chunk_size = 1 << 20
        with open(filename, "wb") as f:
            with tqdm(total=total) as progress:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    f.flush()
                    progress.update(len(chunk))
        print(f"Saved {filename}")
        return True

    def get_path(self, dest):
        return dest / self.filename

    def acquire(self, dest):
        path = self.get_path(dest)
        self.ensure(path)
        success = self.download(self.url, path)
        return success and path


# class FunctionSource(Source):
#     def __init__(self, fn, **kwargs):
#         self.fn = fn
#         self.kwargs = kwargs

#     def acquire(self, dest):
#         self.fn(dest, **self.kwargs)


# TODO: other sources
# TorrentSource: Download using a magnet link, e.g. from AcademicTorrents
# S3Source:      Get from S3 bucket
# GDriveSource:  From Google Drive
# SSHSource:     Using scp or rsync


def unpack_gz(source, dest):
    with gzip.open(source, "rb") as f_in:
        with open(dest, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


shutil.register_unpack_format("gzip", [".gz"], unpack_gz)


archive_extensions = set(
    reduce(list.__add__, (exts for _, exts, *__ in shutil.get_unpack_formats()))
)


class Acquirer:
    def __init__(self, *, sources, dest, cache, unpack=True):
        self.sources = list(sorted(sources, key=lambda src: -src.priority))
        self.dest = _p(dest)
        self.cache = _p(cache)
        self.unpack = unpack

    def get(self):
        if self.dest.exists():
            # TODO: be smarter about this, check the checksum
            return

        for source in self.sources:
            found = source(self.cache)
            if found:
                break
        else:
            return False

        return self._transfer(found)

    def _transfer(self, source):
        if source == self.dest or self.dest.exists():
            return

        self.dest.parent.mkdir(parents=True, exist_ok=True)

        if source.is_file():
            if self.unpack:
                try:
                    shutil.unpack_archive(source, self.dest)
                except shutil.ReadError:
                    # Ignore if format is unsupported
                    pass

            else:
                shutil.copy(source, self.dest)

        else:
            shutil.copytree(source, self.dest)

        return self.dest


def test():
    # from torchvision.datasets import CIFAR10
    import time

    # t1 = time.time()
    # cf = CIFAR10("~/data/tvd", download=True)
    # breakpoint()
    # t2 = time.time()
    # print(t2 - t1)

    t1 = time.time()
    cifar = Acquirer(
        sources=[
            LocalSource("~/data/source/tgz/cifar-10-python.tar.gz"),
            LocalSource("~/data/source/CIFAR"),
            HttpSource("https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"),
        ],
        cache="~/data/cache/CIFAR",
        dest="~/data/data/CIFAR",
        unpack=True,
    )

    cifar.get()

    t2 = time.time()
    print(t2 - t1)


if __name__ == "__main__":
    test()


# mnist = Acquirer(
#     sources=[
#         LocalSource("~/data/source/MNIST/train-images-idx3-ubyte"),
#         HttpSource("http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz"),
#         HttpSource(
#             "https://ossci-datasets.s3.amazonaws.com/mnist/train-images-idx3-ubyte.gz"
#         ),
#     ],
#     cache="~/data/cache/MNIST/train-images-idx3-ubyte.gz",
#     dest="~/data/data/MNIST/train-images-idx3-ubyte",
#     unpack=True,
# )


# mnist.get()
