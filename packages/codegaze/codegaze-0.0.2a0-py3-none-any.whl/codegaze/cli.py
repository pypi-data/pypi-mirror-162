import typer


app = typer.Typer()


@app.command()
def ui(port: int = 8080):
    """
    Launch the CodeGaze UI.
    """
    from codegaze.web.backend.app import launch

    launch(port=port)


@app.command()
def list():
    print("list")


def run():
    app()


if __name__ == "__main__":
    app()
