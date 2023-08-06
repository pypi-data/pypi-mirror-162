import datetime
from .processor import process_language

def myrepl(debug=True):
    code = 1
    while code != "x":
        try:
            # prompt = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            prompt = datetime.datetime.utcnow().isoformat()
            code = input(f"FE {prompt} >> ")
            code = code.strip()
            if code == "bahasa":
                indah4(bahasa, warna="green")
            elif code != "" and code != "x":
                process_language(code, debug=debug)
        except EOFError as eof:
            print("Ctrl+D? Exiting...", eof)
            break
        except Exception as err:
            print(err)


def quick_repl():
    code = 1
    while code != "x":
        try:
            prompt = datetime.datetime.utcnow().isoformat()
            code = input(f"DECL {prompt} >> ")
            code = code.strip()
            if code == "bahasa":
                indah3(bahasa, warna="green")
            elif code != "" and code != "x":
                process_language(code)
        except EOFError as eof:
            print("Ctrl+D? Exiting...", eof)
            break
        except Exception as err:
            print(err)


def main() -> None:
    myrepl()


if __name__ == "__main__":
    main()
