from dotenv import load_dotenv

# Load the repo-root .env before Config reads os.environ. Variables already
# set (Docker, CI, the shell) win over the file. Tests don't import this
# module, so they never pick up a developer's .env.
load_dotenv()

from app import create_app  # noqa: E402

app = create_app()


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000,
    )
