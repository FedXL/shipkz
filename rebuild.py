import docker
import sys


def main():
    client = docker.from_env()

    try:
        print("Starting build process...")
        image, build_logs = client.images.build(path=".", tag="fedxl/storage:shipkz")
        for log in build_logs:
            if 'stream' in log:
                sys.stdout.write(log['stream'])

        print("\nBuild successful, pushing the image...")
        push_logs = client.images.push("fedxl/storage:shipkz", stream=True, decode=True)
        for log in push_logs:
            if 'status' in log:
                print(log['status'])
            if 'error' in log:
                print(log['error'], file=sys.stderr)
                break
        else:
            print("Push successful!")
    except docker.errors.BuildError as build_error:
        print(f"Build failed: {build_error}", file=sys.stderr)
    except docker.errors.APIError as api_error:
        print(f"Push failed: {api_error}", file=sys.stderr)


if __name__ == "__main__":
    main()