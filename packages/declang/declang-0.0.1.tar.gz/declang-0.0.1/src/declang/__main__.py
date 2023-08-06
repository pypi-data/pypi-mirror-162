import datetime, traceback

from langutils.app.printutils import print_json, indah3, indah4, print_copy
from langutils.app.utils import trycopy, env_exist, env_reload
from langutils.app.treeutils import (
    child,
    child1,
    anak,
    jumlahanak,
    beranak,
    data,
    token,
    chtoken,
    chdata,
)
from lark import (
    Lark,
    InlineTransformer,
)

from declang.app.transpiler.frontend.bahasa import bahasa
from declang.app.transpiler.frontend.handler import handler


class TheProcessor(InlineTransformer):
    def declarative_program(self, *item_lines):
        return item_lines


def process_language(code, returning=False, debug=True, current_handler=handler):
    # print('#1 process language, code:', code, 'grammar:', bahasa[:50] + '...')
    try:
        pre_parser = Lark(bahasa, start="declarative_program")
        parser = pre_parser.parse
        indah4("=" * 20 + " " + code + "\n", warna="red")
        parsed_tree = parser(code)
        instructions = TheProcessor().transform(parsed_tree)
        results = []
        for insn in instructions:
            if debug:
                print(insn.pretty())
            hasil = current_handler(insn)
            if hasil is not None:
                # kadang handler gak return value, kita gak perlu print output
                results.append(hasil)

        hasil = ""
        if results:
            print("[app.transpiler.frontend.main] results:", results)
            hasil = "\n".join(results)
        if returning:
            return results
        if hasil:
            indah4(hasil, warna="yellow")
        return results

    except Exception as err:
        print(err)
        trace = traceback.format_exc()
        print(trace)


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
                # print(f'code adlh: [{code}]')
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
            # prompt = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
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
