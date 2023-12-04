import aiodocker
import pathlib
import re


async def start_deepdanbooru(temp_path: str, identifier: str):
    docker = aiodocker.Docker()
    regex = r"\([0-1]\.[0-9][0-9][0-9]\).+"
    print("starting docker container")
    volumes = [f"{pathlib.Path(temp_path).absolute()}:/app/data/"]
    print(volumes)
    tags = []
    # await docker.pull("kamuri/deepdanbooru")
    container = await docker.containers.create_or_replace(
        config={
            "Cmd": [
                "evaluate",
                "--project-path",
                "/app/model",
                "/app/data",
                "--allow-folder",
            ],
            "Image": "kamuri/deepdanbooru",
            "HostConfig": {
                "Binds": volumes,
            },
        },
        name=f"deepdanbooru_web_{identifier}",
    )
    await container.start()
    await container.wait(timeout=60)
    async for x in container.log(stdout=True, stderr=True, follow=True):
        line = x.strip("\n")
        if re.match(regex, line):
            tags.append(line.split(" ")[1])
    await container.delete(force=True)
    await docker.close()
    return tags
