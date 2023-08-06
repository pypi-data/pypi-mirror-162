import typer
import subprocess
import os
import users

app = typer.Typer()


@app.command()
def startapp(name: str):
    if os.path.exists(name):
       print(f"dir ({name}) all ready exist")
    else:
        os.makedirs(name)
        with open(f"./{name}/__init__.py", "w") as file:
            file.write('')
        with open(f"./{name}/apps.py", "w") as file:
            file.write(users.apps)
    #subprocess.run('ls')



@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")




if __name__ == "__main__":
    app()
    

