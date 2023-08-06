from kubernetes import client


def use_shared_memory_to_volume(op):
    name = "dhsm"
    op.add_volume(
        client.V1Volume(
            name=name, empty_dir=client.V1EmptyDirVolumeSource(medium="Memory")
        )
    ).add_volume_mount(client.V1VolumeMount(name=name, mount_path="/dev/shm"))
    return op
